from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import os

# Importar las funciones de nuestro app.py
from app import index_project, generate_prd_and_user_stories, get_next_chat_question

app = FastAPI()

# Montar el directorio de archivos estáticos (CSS, JS, etc. si los hubiera más adelante)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar las plantillas Jinja2 para servir HTML
templates = Jinja2Templates(directory="templates")

# Almacenamiento temporal para el índice y el historial de conversación (en una app real se usaría una DB)
project_index = None # Este será el índice global que se cargará/creará
conversation_data: Dict[str, List[Dict[str, str]]] = {}

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
    global project_index, indexed_project_path
    project_path = input_data.project_path
    force_index = input_data.force_index

    try:
        # Intentar cargar o crear el índice
        project_index = await index_project(project_path, force_index)
        indexed_project_path = project_path # Guardar la ruta del proyecto indexado
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
    global project_index, conversation_data
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
        return {"status": "success", "prd": prd_content, "user_stories": user_stories_content, "technical_plan": technical_plan_content}
    except Exception as e:
        print(f"DEBUG: Exception caught in generate_documents_endpoint: {type(e)} - {e}")
        return {"status": "error", "message": f"Error al generar documentos: {str(e)}"}

# Para ejecutar esta aplicación, guarda este archivo como main.py y ejecuta:
# uvicorn main:app --reload 