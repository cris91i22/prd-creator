from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import os

# Importar las funciones de nuestro app.py
from app import index_project, generate_prd_and_user_stories, get_next_chat_question, get_developer_chat_response, summarize_developer_chat, generate_code_agent_brief

app = FastAPI()

# Montar el directorio de archivos estáticos (CSS, JS, etc. si los hubiera más adelante)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar las plantillas Jinja2 para servir HTML
templates = Jinja2Templates(directory="templates")

# Almacenamiento temporal para el índice y el historial de conversación (en una app real se usaría una DB)
project_index = None # Este será el índice global que se cargará/creará
conversation_data: Dict[str, List[Dict[str, str]]] = {}
developer_chat_history_data: Dict[str, List[Dict[str, str]]] = {} # Nuevo: Historial del chat de desarrolladores
generated_documents_cache: Dict[str, Dict[str, str]] = {} # Nuevo: Cache para PRD, HU, Plan Técnico
gitingest_tree_cache: Dict[str, Dict] = {} # Nuevo: Cache para el árbol de archivos de gitingest

# Variable global para almacenar la ruta del proyecto indexado
indexed_project_path: str = ""

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Sirve la página HTML principal de la aplicación."""
    return templates.TemplateResponse("index.html", {"request": request})

class ProjectPathInput(BaseModel):
    project_path: str
    force_index: bool = False

@app.post("/index_project")
async def index_project_endpoint(input_data: ProjectPathInput):
    global project_index, indexed_project_path, gitingest_tree_cache
    project_path = input_data.project_path
    force_index = input_data.force_index
    session_id = "default_user_session" # Assuming a default session ID for now

    try:
        # Intentar cargar o crear el índice
        project_index, gitingest_tree = await index_project(project_path, force_index)
        indexed_project_path = project_path # Guardar la ruta del proyecto indexado
        gitingest_tree_cache[session_id] = gitingest_tree # Store the tree
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
    global project_index, conversation_data, indexed_project_path
    initial_description = input_data.initial_description
    template_type = input_data.template_type
    existing_prd_content = input_data.existing_prd_content
    llm_provider = input_data.llm_provider


    # Asegurarse de que el proyecto esté indexado antes de iniciar la conversación
    if project_index is None and indexed_project_path:
        try:
            # Intentar cargar el índice si la aplicación se reinició
            project_index = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "Por favor, indexa un proyecto primero."}

    session_id = "default_user_session"
    conversation_data[session_id] = []
    # El primer mensaje ahora incluirá el tipo de template y el PRD existente
    conversation_data[session_id].append({
        "role": "pm", 
        "content": initial_description,
        "template_type": template_type,
        "existing_prd_content": existing_prd_content,
        "llm_provider": llm_provider # Store LLM provider in conversation history
    })

    # Generar la primera pregunta dinámicamente
    try:
        first_question = await get_next_chat_question(
            conversation_data[session_id], 
            project_index,
            template_type,
            existing_prd_content,
            llm_provider # Pass llm_provider
        )
        conversation_data[session_id].append({"role": "ia", "content": first_question})
        return {"status": "success", "message": first_question, "session_id": session_id}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar la primera pregunta: {str(e)}"}

class ChatMessageInput(BaseModel):
    session_id: str
    user_message: str
    llm_provider: str = "google" # Add llm_provider to ChatMessageInput

@app.post("/send_message")
async def send_message_endpoint(message_data: ChatMessageInput):
    global project_index, conversation_data, indexed_project_path
    session_id = message_data.session_id
    user_message = message_data.user_message
    llm_provider = message_data.llm_provider # Get llm_provider

    if session_id not in conversation_data:
        return {"status": "error", "message": "Sesión no encontrada."}

    # Asegurarse de que el proyecto esté indexado
    if project_index is None and indexed_project_path:
        try:
            project_index = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "El proyecto no ha sido indexado aún."}

    # Añadir mensaje del usuario al historial
    conversation_data[session_id].append({"role": "pm", "content": user_message})
    current_conversation = conversation_data[session_id]

    # Generar la siguiente respuesta de la IA dinámicamente
    try:
        # Recuperar el template_type y existing_prd_content del primer mensaje en conversation_data
        # Esto asume que el primer mensaje siempre contiene esta información
        first_message = current_conversation[0]
        template_type = first_message.get("template_type", "feature.md") # Valor por defecto
        existing_prd_content = first_message.get("existing_prd_content") # Puede ser None
        # llm_provider is passed directly from the client for send_message

        ai_response = await get_next_chat_question(
            current_conversation, 
            project_index,
            template_type,
            existing_prd_content,
            llm_provider # Pass llm_provider
        )
        conversation_data[session_id].append({"role": "ia", "content": ai_response})
        return {"status": "success", "ai_response": ai_response}
    except Exception as e:
        return {"status": "error", "message": f"Error al generar la respuesta de la IA: {str(e)}"}

class GenerateDocumentsInput(BaseModel):
    session_id: str
    template_type: str
    existing_prd_content: Optional[str] = None
    llm_provider: str = "google" # Add llm_provider to GenerateDocumentsInput

@app.post("/generate_documents")
async def generate_documents_endpoint(data: GenerateDocumentsInput):
    global project_index, conversation_data, generated_documents_cache # Add generated_documents_cache
    session_id = data.session_id
    template_type = data.template_type
    existing_prd_content = data.existing_prd_content
    llm_provider = data.llm_provider # Get llm_provider

    current_conversation = conversation_data.get(session_id)
    if not current_conversation or not project_index:
        return {"status": "error", "message": "Sesión no encontrada o proyecto no indexado."}

    # Debugging: Imprimir el contenido de conversation_history
    print(f"DEBUG: Received conversation_history type: {type(current_conversation)}")
    print(f"DEBUG: Received conversation_history: {current_conversation}")
    print(f"DEBUG: Received template_type: {template_type}")
    print(f"DEBUG: Received existing_prd_content (len): {len(existing_prd_content) if existing_prd_content else 'None'}")
    print(f"DEBUG: Received llm_provider: {llm_provider}") # Debugging for llm_provider


    # Generar PRD e Historias de Usuario (usando la función de app.py)
    try:
        prd_content, user_stories_content, technical_plan_content = await generate_prd_and_user_stories(
            current_conversation, 
            project_index, 
            template_type,
            existing_prd_content,
            llm_provider # Pass llm_provider
        )
        
        # Store generated documents in cache for developer chat
        generated_documents_cache[session_id] = {
            "prd": prd_content,
            "user_stories": user_stories_content,
            "technical_plan": technical_plan_content
        }
        # Initialize developer chat history for this session
        developer_chat_history_data[session_id] = []

        return {"status": "success", "prd": prd_content, "user_stories": user_stories_content, "technical_plan": technical_plan_content}
    except Exception as e:
        print(f"DEBUG: Exception caught in generate_documents_endpoint: {type(e)} - {e}")
        return {"status": "error", "message": f"Error al generar documentos: {str(e)}"}

class DeveloperChatMessageInput(BaseModel):
    session_id: str
    developer_message: str
    llm_provider: str = "google"

@app.post("/developer_chat")
async def developer_chat_endpoint(message_data: DeveloperChatMessageInput):
    global project_index, developer_chat_history_data, generated_documents_cache, indexed_project_path
    session_id = message_data.session_id
    developer_message = message_data.developer_message
    llm_provider = message_data.llm_provider

    if session_id not in developer_chat_history_data:
        return {"status": "error", "message": "Sesión de chat de desarrollador no encontrada. Por favor, genera los documentos primero."}
    
    if session_id not in generated_documents_cache:
        return {"status": "error", "message": "Documentos generados no encontrados para esta sesión. Por favor, genera los documentos primero."}

    # Ensure project is indexed
    if project_index is None and indexed_project_path:
        try:
            project_index = await index_project(indexed_project_path)
        except Exception as e:
            return {"status": "error", "message": f"Error al recargar el índice del proyecto: {str(e)}. Por favor, re-indexa el proyecto."}
    elif project_index is None:
        return {"status": "error", "message": "El proyecto no ha sido indexado aún."}

    # Add developer message to history
    developer_chat_history_data[session_id].append({"role": "developer", "content": developer_message})
    current_dev_chat = developer_chat_history_data[session_id]
    
    # Get generated documents
    documents = generated_documents_cache[session_id]
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
        developer_chat_history_data[session_id].append({"role": "ia", "content": ai_response})
        return {"status": "success", "ai_response": ai_response}
    except Exception as e:
        print(f"DEBUG: Error in developer_chat_endpoint: {type(e)} - {e}")
        return {"status": "error", "message": f"Error al generar respuesta del chat de desarrollador: {str(e)}"}

class SummarizeDeveloperChatInput(BaseModel):
    session_id: str
    llm_provider: str = "google"

@app.post("/summarize_developer_chat")
async def summarize_developer_chat_endpoint(data: SummarizeDeveloperChatInput):
    global developer_chat_history_data
    session_id = data.session_id
    llm_provider = data.llm_provider

    developer_chat = developer_chat_history_data.get(session_id)
    if not developer_chat:
        return {"status": "error", "message": "No hay historial de chat de desarrollador para resumir."}
    
    try:
        summary = await summarize_developer_chat(developer_chat, llm_provider)
        return {"status": "success", "summary": summary}
    except Exception as e:
        print(f"DEBUG: Error in summarize_developer_chat_endpoint: {type(e)} - {e}")
        return {"status": "error", "message": f"Error al generar resumen para Jira: {str(e)}"}

class GenerateCodeAgentBriefInput(BaseModel):
    session_id: str
    llm_provider: str = "google"

@app.post("/generate_code_agent_brief")
async def generate_code_agent_brief_endpoint(data: GenerateCodeAgentBriefInput):
    global project_index, developer_chat_history_data, generated_documents_cache, indexed_project_path
    session_id = data.session_id
    llm_provider = data.llm_provider

    developer_chat = developer_chat_history_data.get(session_id)
    if not developer_chat:
        return {"status": "error", "message": "No hay historial de chat de desarrollador para generar el brief."}
    
    documents = generated_documents_cache.get(session_id)
    if not documents:
        return {"status": "error", "message": "Documentos generados no encontrados para esta sesión."}

    # Ensure project is indexed
    if project_index is None and indexed_project_path:
        try:
            project_index = await index_project(indexed_project_path)
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
        print(f"DEBUG: Error in generate_code_agent_brief_endpoint: {type(e)} - {e}")
        return {"status": "error", "message": f"Error al generar brief para el agente de código: {str(e)}"}

@app.get("/get_structured_documents")
async def get_structured_documents_endpoint(session_id: str):
    global generated_documents_cache
    documents = generated_documents_cache.get(session_id)

    if not documents:
        return JSONResponse(content={"status": "error", "message": "Documentos no encontrados para la sesión."},
                            status_code=404)

    # Simple splitting by lines for now. Can be enhanced later to parse markdown headings.
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
    global gitingest_tree_cache
    tree_data = gitingest_tree_cache.get(session_id)
    if not tree_data:
        return JSONResponse(content={"status": "error", "message": "Árbol de gitingest no encontrado para la sesión."},
                            status_code=404)
    return JSONResponse(content={"status": "success", "tree": tree_data})

# Para ejecutar esta aplicación, guarda este archivo como main.py y ejecuta:
# uvicorn main:app --reload 