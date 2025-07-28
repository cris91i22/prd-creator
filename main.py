from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import redis.asyncio as redis
import json

# Importar las funciones de nuestro app.py
from app import index_project, generate_prd_and_user_stories, get_next_chat_question, get_developer_chat_response, summarize_developer_chat, generate_code_agent_brief
from corporate.figma.analyzer import FigmaDesignAnalyzer

app = FastAPI()

# Configuración de Redis
redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost"))

# Montar el directorio de archivos estáticos (CSS, JS, etc. si los hubiera más adelante)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar las plantillas Jinja2 para servir HTML
templates = Jinja2Templates(directory="templates")

# Almacenamiento temporal para el índice y el historial de conversación (en una app real se usaría una DB)
project_index = None # Este será el índice global que se cargará/creará

# --- Redis Helper Functions ---

async def get_redis_list(key: str) -> List[Dict]:
    """Retrieves a list of dictionaries from a Redis key."""
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return []

async def set_redis_list(key: str, data: List[Dict]):
    """Saves a list of dictionaries to a Redis key."""
    await redis_client.set(key, json.dumps(data))

async def append_to_redis_list(key: str, item: Dict):
    """Appends a dictionary to a list in Redis."""
    current_list = await get_redis_list(key)
    current_list.append(item)
    await set_redis_list(key, current_list)

async def get_redis_dict(key: str) -> Dict:
    """Retrieves a dictionary from a Redis key."""
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return {}

# Initialize Figma analyzer
figma_analyzer = FigmaDesignAnalyzer()

class AnalyzeDesignInput(BaseModel):
    session_id: str
    figma_link: str

@app.post("/analyze_design")
async def analyze_design_endpoint(data: AnalyzeDesignInput):
    """
    Endpoint para analizar un diseño de Figma y extraer información relevante
    del Design System para el contexto de la IA.
    """
    session_id = data.session_id
    design_context_key = f"design_context:{session_id}"
    
    try:
        # Analizar el enlace de Figma
        design_context = await figma_analyzer.analyze_figma_link(data.figma_link)
        
        # Generar contexto técnico
        technical_context = figma_analyzer.generate_technical_context(design_context)
        
        # Guardar el contexto en Redis
        await set_redis_dict(design_context_key, {
            "full_context": design_context,
            "technical_context": technical_context
        })
        
        return {
            "status": "success",
            "technical_context": technical_context
        }
    except Exception as e:
        return {"status": "error", "message": f"Error al analizar el diseño: {str(e)}"}
        return json.loads(data)
    return {}

async def set_redis_dict(key: str, data: Dict):
    """Saves a dictionary to a Redis key."""
    await redis_client.set(key, json.dumps(data))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Sirve la página HTML principal de la aplicación."""
    return templates.TemplateResponse("index.html", {"request": request})

class ProjectPathInput(BaseModel):
    project_path: str
    force_index: bool = False

@app.post("/index_project")
async def index_project_endpoint(input_data: ProjectPathInput):
    global project_index, indexed_project_path
    project_path = input_data.project_path
    force_index = input_data.force_index
    session_id = "default_user_session" # Assuming a default session ID for now

    try:
        # Intentar cargar o crear el índice
        project_index, gitingest_tree = await index_project(project_path, force_index)
        indexed_project_path = project_path # Guardar la ruta del proyecto indexado
        await set_redis_dict(f"gitingest_tree:{session_id}", gitingest_tree)
        return JSONResponse(content={"message": "Proyecto indexado con éxito."})
    except Exception as e:
        return JSONResponse(content={"detail": f"Error durante la indexación: {str(e)}"}, status_code=500)

class StartConversationInput(BaseModel):
    initial_description: Optional[str] = None
    template_type: str
    existing_prd_content: Optional[str] = None
    llm_provider: str = "google"

@app.post("/start_conversation")
async def start_conversation_endpoint(input_data: StartConversationInput):
    global project_index, indexed_project_path
    initial_description = input_data.initial_description
    template_type = input_data.template_type
    existing_prd_content = input_data.existing_prd_content
    llm_provider = input_data.llm_provider


    # Asegurarse de que el proyecto esté indexado antes de iniciar la conversación
    if project_index is None and indexed_project_path:
        try:
            # Intentar cargar el índice si la aplicación se reinició
            project_index, _ = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "Por favor, indexa un proyecto primero."}

    session_id = "default_user_session"
    conversation_key = f"conversation:{session_id}"
    
    initial_message = {
        "role": "pm", 
        "content": initial_description,
        "template_type": template_type,
        "existing_prd_content": existing_prd_content,
        "llm_provider": llm_provider
    }
    await set_redis_list(conversation_key, [initial_message])

    # Generar la primera pregunta dinámicamente
    try:
        conversation_history = await get_redis_list(conversation_key)
        first_question = await get_next_chat_question(
            conversation_history, 
            project_index,
            template_type,
            existing_prd_content,
            llm_provider
        )
        await append_to_redis_list(conversation_key, {"role": "ia", "content": first_question})
        return {"status": "success", "message": first_question, "session_id": session_id}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar la primera pregunta: {str(e)}"}

class ChatMessageInput(BaseModel):
    session_id: str
    user_message: str
    llm_provider: str = "google"

@app.post("/send_message")
async def send_message_endpoint(message_data: ChatMessageInput):
    global project_index, indexed_project_path
    session_id = message_data.session_id
    user_message = message_data.user_message
    llm_provider = message_data.llm_provider
    conversation_key = f"conversation:{session_id}"

    if not await redis_client.exists(conversation_key):
        return {"status": "error", "message": "Sesión no encontrada."}

    # Asegurarse de que el proyecto esté indexado
    if project_index is None and indexed_project_path:
        try:
            project_index, _ = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "El proyecto no ha sido indexado aún."}

    # Añadir mensaje del usuario al historial
    await append_to_redis_list(conversation_key, {"role": "pm", "content": user_message})
    current_conversation = await get_redis_list(conversation_key)

    # Generar la siguiente respuesta de la IA dinámicamente
    try:
        first_message = current_conversation[0]
        template_type = first_message.get("template_type", "feature.md")
        existing_prd_content = first_message.get("existing_prd_content")

        ai_response = await get_next_chat_question(
            current_conversation, 
            project_index,
            template_type,
            existing_prd_content,
            llm_provider
        )
        await append_to_redis_list(conversation_key, {"role": "ia", "content": ai_response})
        return {"status": "success", "ai_response": ai_response}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar la respuesta de la IA: {str(e)}"}

class GenerateDocumentsInput(BaseModel):
    session_id: str
    template_type: str
    existing_prd_content: Optional[str] = None
    llm_provider: str = "google"

@app.post("/generate_documents")
async def generate_documents_endpoint(data: GenerateDocumentsInput):
    global project_index
    session_id = data.session_id
    template_type = data.template_type
    existing_prd_content = data.existing_prd_content
    llm_provider = data.llm_provider
    conversation_key = f"conversation:{session_id}"
    documents_key = f"documents:{session_id}"
    dev_chat_key = f"developer_chat:{session_id}"

    current_conversation = await get_redis_list(conversation_key)
    if not current_conversation or not project_index:
        return {"status": "error", "message": "Sesión no encontrada o proyecto no indexado."}

    try:
        prd_content, user_stories_content, technical_plan_content = await generate_prd_and_user_stories(
            current_conversation, 
            project_index, 
            template_type,
            existing_prd_content,
            llm_provider
        )
        
        documents = {
            "prd": prd_content,
            "user_stories": user_stories_content,
            "technical_plan": technical_plan_content
        }
        await set_redis_dict(documents_key, documents)
        await set_redis_list(dev_chat_key, []) # Initialize developer chat history

        return {"status": "success", "prd": prd_content, "user_stories": user_stories_content, "technical_plan": technical_plan_content}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar documentos: {str(e)}"}

class DeveloperChatMessageInput(BaseModel):
    session_id: str
    developer_message: str
    llm_provider: str = "google"

@app.post("/developer_chat")
async def developer_chat_endpoint(message_data: DeveloperChatMessageInput):
    global project_index, indexed_project_path
    session_id = message_data.session_id
    developer_message = message_data.developer_message
    llm_provider = message_data.llm_provider
    dev_chat_key = f"developer_chat:{session_id}"
    documents_key = f"documents:{session_id}"

    if not await redis_client.exists(dev_chat_key):
        return {"status": "error", "message": "Sesión de chat de desarrollador no encontrada. Por favor, genera los documentos primero."}
    
    if not await redis_client.exists(documents_key):
        return {"status": "error", "message": "Documentos generados no encontrados para esta sesión. Por favor, genera los documentos primero."}

    if project_index is None and indexed_project_path:
        try:
            project_index, _ = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "El proyecto no ha sido indexado aún."}

    await append_to_redis_list(dev_chat_key, {"role": "developer", "content": developer_message})
    current_dev_chat = await get_redis_list(dev_chat_key)
    
    documents = await get_redis_dict(documents_key)
    prd_content = documents.get("prd", "")
    user_stories_content = documents.get("user_stories", "")
    technical_plan_content = documents.get("technical_plan", "")

    try:
        ai_response = await get_developer_chat_response(
            current_dev_chat,
            project_index,
            prd_content,
            user_stories_content,
            technical_plan_content,
            llm_provider
        )
        await append_to_redis_list(dev_chat_key, {"role": "ia", "content": ai_response})
        return {"status": "success", "ai_response": ai_response}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar respuesta del chat de desarrollador: {str(e)}"}

class SummarizeDeveloperChatInput(BaseModel):
    session_id: str
    llm_provider: str = "google"

@app.post("/summarize_developer_chat")
async def summarize_developer_chat_endpoint(data: SummarizeDeveloperChatInput):
    session_id = data.session_id
    llm_provider = data.llm_provider
    dev_chat_key = f"developer_chat:{session_id}"

    developer_chat = await get_redis_list(dev_chat_key)
    if not developer_chat:
        return {"status": "error", "message": "No hay historial de chat de desarrollador para resumir."}
    
    try:
        summary = await summarize_developer_chat(developer_chat, llm_provider)
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar resumen para Jira: {str(e)}"}

class GenerateCodeAgentBriefInput(BaseModel):
    session_id: str
    llm_provider: str = "google"

@app.post("/generate_code_agent_brief")
async def generate_code_agent_brief_endpoint(data: GenerateCodeAgentBriefInput):
    global project_index, indexed_project_path
    session_id = data.session_id
    llm_provider = data.llm_provider
    dev_chat_key = f"developer_chat:{session_id}"
    documents_key = f"documents:{session_id}"

    developer_chat = await get_redis_list(dev_chat_key)
    if not developer_chat:
        return {"status": "error", "message": "No hay historial de chat de desarrollador para generar el brief."}
    
    documents = await get_redis_dict(documents_key)
    if not documents:
        return {"status": "error", "message": "Documentos generados no encontrados para esta sesión."}

    if project_index is None and indexed_project_path:
        try:
            project_index, _ = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "El proyecto no ha sido indexado aún."}

    try:
        brief = await generate_code_agent_brief(
            developer_chat,
            project_index,
            documents.get("prd", ""),
            documents.get("user_stories", ""),
            documents.get("technical_plan", ""),
            llm_provider
        )
        return {"status": "success", "brief": brief}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar brief para el agente de código: {str(e)}"}

@app.get("/get_structured_documents")
async def get_structured_documents_endpoint(session_id: str):
    documents_key = f"documents:{session_id}"
    documents = await get_redis_dict(documents_key)

    if not documents:
        return JSONResponse(content={"status": "error", "message": "Documentos no encontrados para la sesión."},
                            status_code=404)

    structured_prd = [line for line in documents.get("prd", "").splitlines() if line.strip()]
    structured_user_stories = [line for line in documents.get("user_stories", "").splitlines() if line.strip()]
    structured_technical_plan = [line for line in documents.get("technical_plan", "").splitlines() if line.strip()]

    return {
        "status": "success",
        "prd_lines": structured_prd,
        "user_stories_lines": structured_user_stories,
        "technical_plan_lines": structured_technical_plan
    }

@app.get("/get_gitingest_tree")
async def get_gitingest_tree_endpoint(session_id: str):
    tree_key = f"gitingest_tree:{session_id}"
    tree_data = await get_redis_dict(tree_key)
    if not tree_data:
        return JSONResponse(content={"status": "error", "message": "Árbol de gitingest no encontrado para la sesión."},
                            status_code=404)
    return JSONResponse(content={"status": "success", "tree": tree_data})

# Para ejecutar esta aplicación, guarda este archivo como main.py y ejecuta:
# uvicorn main:app --reload 