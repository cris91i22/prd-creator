# app.py
# Este archivo contendrá el backend de la aplicación para generar PRDs e Historias de Usuario.

import os
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.schema import Document
import chromadb
from gitingest import ingest_async
from typing import List, Dict, Optional
from dotenv import load_dotenv
load_dotenv()

# --- Configuración de API Keys ---
# Asegúrate de configurar tu GOOGLE_API_KEY como variable de entorno
# os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI" 
# La línea de abajo es para fines de demostración, en producción usa variables de entorno seguras.
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# --- Fase 1: Indexación y Contextualización del Proyecto Local ---

async def index_project(project_path: str, force_index: bool = False):
    """
    Función para indexar el proyecto local.
    Pasos:
    1. Ejecutar gitingest sobre project_path para obtener una representación del código.
    2. Aplicar chunking con LlamaIndex.
    3. Generar embeddings con GoogleGenAIEmbedding.
    4. Almacenar en ChromaDB.
    """
    print(f"Iniciando indexación del proyecto en: {project_path}")

    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection_name = "project_index"
    
    # Verificar si el índice ya existe y si no se ha solicitado una indexación forzada
    if not force_index and db.count_collections() > 0: # Check if any collection exists to avoid error if 'project_index' isn't the only one
        try:
            chroma_collection = db.get_collection(chroma_collection_name)
            if chroma_collection.count() > 0: # Check if the specific collection has data
                print("Cargando índice existente de ChromaDB...")
                vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
                embed_model = GoogleGenAIEmbedding(model_name="text-embedding-004")
                index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=embed_model
                )
                print("Índice existente de ChromaDB cargado con éxito.")
                # We need to retrieve the original tree if we're loading from existing.
                # For now, we'll return a placeholder or re-ingest if not found easily.
                # A more robust solution would store the tree in ChromaDB as well.
                # For this task, we'll assume a fresh ingest is fine for now if not found easily.
                
                # To simplify for now, if we loaded from existing, we don't have the tree readily available.
                # In a real app, you might store it. For this feature, let's re-ingest to get the tree
                # even if the index exists, or add a way to store/retrieve the tree.
                # For simplicity, if we hit this, let's assume we re-ingest to get the tree.
                # TODO: Improve this to actually load the tree from storage if index exists.
                print("Re-ingesting project to retrieve file tree for existing index...")
                summary, tree, gitingest_content = await ingest_async(project_path)
                return index, tree
        except Exception as e:
            print(f"No se pudo cargar el índice existente o la colección no existe (error: {e}). Procediendo con la indexación.")
            # If there's an error loading, we'll proceed to re-index.

    print("Creando o re-indexando el proyecto...")
    # Paso 1: Ejecutar gitingest
    try:
        print(f"Procesando el proyecto con gitingest: {project_path}")
        summary, tree, gitingest_content = await ingest_async(project_path)
        print("gitingest completado. Contenido extraído.")
    except Exception as e:
        print(f"Error al ejecutar gitingest: {e}")
        gitingest_content = "Este es un contenido de fallback porque gitingest falló o no se pudo ejecutar. Asegúrate de que el directorio del proyecto exista y sea válido."
        tree = {"name": "Error: Could not retrieve file tree.", "type": "dir", "children": []} # Fallback tree
    
    # Ensure gitingest_content is a string, even if ingest_async somehow returns None
    if gitingest_content is None:
        gitingest_content = "No content extracted by gitingest."

    # Convertir el contenido de gitingest a un objeto Document de LlamaIndex
    documents = [Document(text=gitingest_content)]

    # Paso 2: Aplicar chunking con LlamaIndex
    node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"Documento dividido en {len(nodes)} chunks.")

    # Paso 3: Generar embeddings con GoogleGenAIEmbedding
    embed_model = GoogleGenAIEmbedding(model_name="text-embedding-004")

    # Paso 4: Almacenar en ChromaDB
    # Si llegamos aquí, significa que necesitamos crear o re-crear el índice.
    # Asegurémonos de tener la colección correcta.
    chroma_collection = db.get_or_create_collection(chroma_collection_name)
    
    # Es importante borrar los datos existentes si estamos forzando la indexación
    # o si no pudimos cargar un índice válido.
    if chroma_collection.count() > 0 and (force_index or "No se pudo cargar" in e.__str__()): # Simple check for re-index reason
        print(f"Limpiando {chroma_collection.count()} elementos existentes en ChromaDB para re-indexar...")
        chroma_collection.delete(where={}) # Borrar todos los datos

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes, 
        storage_context=storage_context, 
        embed_model=embed_model
    )
    print("Proyecto indexado y embeddings almacenados en ChromaDB.")
    return index, tree

def _is_initial_conversation_state(conversation_history: List[Dict[str, str]]) -> bool:
    """
    Checks if the conversation is at its initial state.
    This is true if there's no history or only a single message from the PM.
    """
    return not conversation_history or \
           (len(conversation_history) == 1 and conversation_history[0].get("role") == "pm")

from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama # Added for Ollama

def _get_llm(llm_provider: str):
    if llm_provider == "google":
        return GoogleGenAI(model="models/gemini-2.5-flash", max_output_tokens=8000)
    elif llm_provider == "ollama":
        return Ollama(model="gemma3n:e2b", request_timeout=360.0)
    else:
        raise ValueError("Invalid LLM provider specified.")


# --- Fase 2: Descripción de Funcionalidad e Interacción Conversacional ---

async def get_next_chat_question(conversation_history: List[Dict[str, str]], project_index, template_type: str, existing_prd_content: Optional[str] = None, llm_provider: str = "google"):
    """
    Genera la siguiente pregunta para el PM basada en el historial de conversación
    y el contexto del proyecto, utilizando un LLM.
    """
    llm = _get_llm(llm_provider)

    # Initialize as string, not PromptTemplate
    full_prompt_content_string = _load_template_content("templates/prompts/base_chat_prompt.txt")

    if _is_initial_conversation_state(conversation_history):
        # Si es el inicio de la conversación o solo el primer mensaje del PM
        if template_type == 'prd_feature_existing':
            full_prompt_content_string += f"""
            El PM ha proporcionado el siguiente contenido de PRD existente:
            {existing_prd_content}
            Tu objetivo es ayudar a desglosar este PRD en Historias de Usuario detalladas.
            Para empezar, ¿en qué funcionalidades o secciones del PRD existente deberíamos enfocarnos para generar las Historias de Usuario?
            """
        elif template_type == 'prd.md' or template_type == 'feature.md':
            full_prompt_content_string += """
            Para empezar, ¿cuál es el problema principal que esta funcionalidad busca resolver para el usuario, o cuál es el objetivo principal que queremos lograr con esta nueva característica?
            """
        else:
            # Default for other templates if needed
            full_prompt_content_string += """
            Para empezar, ¿cuál es el problema o el objetivo principal de lo que estamos discutiendo?
            """
    else:
        if template_type == 'prd_feature_existing':
            # Adaptar el prompt para el caso de PRD Feature
            full_prompt_content_string += f"""
            El PM ha proporcionado el siguiente contenido de PRD existente:
            {existing_prd_content}
            Tu objetivo es ayudar a desglosar este PRD en Historias de Usuario detalladas.
            """
        elif template_type == 'prd.md':
            full_prompt_content_string += """
            Tu objetivo es recopilar suficiente información para generar un PRD completamente nuevo.
            """
        elif template_type == 'feature.md': # This is the default behavior.
            full_prompt_content_string += """
            Tu objetivo es recopilar suficiente información para generar un PRD y Historias de Usuario para una nueva funcionalidad.
            """
        # Add other template type specific instructions here if needed

    full_prompt_content_string += """
        Siguiente pregunta para el PM:
        """

    # Create PromptTemplate from the final string
    prompt_template = PromptTemplate(full_prompt_content_string)

    relevant_project_info = _get_relevant_project_info(project_index, conversation_history, "formular la siguiente pregunta al PM")

    full_prompt_text = prompt_template.format(
        conversation_context="\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history]),
        project_info=relevant_project_info
    )

    try:
        llm_response = await llm.acomplete(full_prompt_text)
        return llm_response.text.strip()
    except Exception as e:
        return f"Error al generar la pregunta con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."


def _get_relevant_project_info(project_index, conversation_history: List[Dict[str, str]], purpose: str) -> str:
    """
    Retrieves relevant project information based on the project index and conversation history.
    The 'purpose' string helps to formulate a more specific query to the project index.
    """
    if project_index:
        try:
            query_engine = project_index.as_query_engine()
            # Usar una consulta más general para el contexto
            simulated_query = f"Dadas las funcionalidades mencionadas en la conversación, ¿qué información técnica relevante del proyecto podría necesitar para {purpose}?"
            response = query_engine.query(simulated_query)
            if response and response.response:
                return response.response
            else:
                return "No se encontró información relevante del proyecto para esta consulta específica."
        except Exception as e:
            return f"Error al recuperar información del proyecto para {purpose}: {str(e)}"
    return "No se recuperó información específica del proyecto para el contexto de la pregunta."


def _load_template_content(template_file: str) -> str:
    """
    Loads the content of a template file from the templates directory.
    """
    full_path = template_file
    try:
        with open(full_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The template file '{full_path}' was not found.")
        return ""
    except Exception as e:
        print(f"Error reading the template file '{full_path}': {e}")
        return ""


# --- Fase 3: Generación de PRDs e Historias de Usuario ---

async def generate_prd_and_user_stories(conversation_history: List[Dict[str, str]], project_index, template_type: str, existing_prd_content: Optional[str] = None, llm_provider: str = "google"):
    """
    Genera el PRD y las historias de usuario.
    En una aplicación real, aquí se usaría un LLM (ej. Gemini-Pro)
    con todo el contexto y posiblemente plantillas.
    """
    print("\n--- Generando PRD e Historias de Usuario ---")

    # Cargar el contenido del template seleccionado

    template_content = ""
    if template_type == 'prd_feature_existing':
        template_content = existing_prd_content if existing_prd_content else ""
        print("Usando contenido de PRD existente para generación.")
    else:
        template_content = _load_template_content(os.path.join("templates", template_type))
        print(f"Template '{template_type}' cargado con éxito.")

    # Combinar todo el contexto para el LLM
    full_context = ""
    for msg in conversation_history:
        if msg['role'] == 'pm': # Only include messages from the Product Manager
            full_context += f"{msg['role'].upper()}: {msg['content']}\n"

    # Simulación de la generación del PRD y HU
    # Utilizaremos un LLM real para la generación
    llm = _get_llm(llm_provider)

    # Plantilla para el PRD

    prd_prompt_content = _load_template_content("templates/prompts/prd_prompt.txt")
    prd_template = PromptTemplate(prd_prompt_content)

    user_stories_prompt_content = _load_template_content("templates/prompts/user_stories_prompt.txt")
    user_stories_template = PromptTemplate(user_stories_prompt_content)


    # Simular la recuperación de información relevante del proyecto
    relevant_project_info = _get_relevant_project_info(project_index, conversation_history, "la implementación")

    # Generar el PRD usando el LLM
    prd_content = ""
    try:
        full_prompt_text_prd = prd_template.format(
            template_content=template_content,
            conversation_context=full_context,
            project_info=relevant_project_info
        )
        llm_response_prd = await llm.acomplete(full_prompt_text_prd)
        prd_content = llm_response_prd.text.strip()
    except Exception as e:
        print(f"DEBUG: Error al generar PRD - Tipo: {type(e).__name__}, Mensaje: {e}")
        prd_content = f"Error al generar el PRD con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."

    # Generar las Historias de Usuario usando el LLM
    user_stories_content = ""
    try:
        full_prompt_text_us = user_stories_template.format(
            prd_content_for_us=prd_content, # Pass the generated PRD as context for User Stories
            conversation_context=full_context,
            project_info=relevant_project_info
        )
        llm_response_us = await llm.acomplete(full_prompt_text_us)
        user_stories_content = llm_response_us.text.strip()

        # Add a heading for User Stories if not present
        if not user_stories_content.startswith("# Historias de Usuario"):
            user_stories_content = "# Historias de Usuario\n" + user_stories_content

    except Exception as e:
        print(f"DEBUG: Error al generar Historias de Usuario - Tipo: {type(e).__name__}, Mensaje: {e}")
        user_stories_content = f"Error al generar las Historias de Usuario con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."

    # Generar el Plan Técnico
    technical_plan_content = await generate_technical_plan(
        conversation_history,
        project_index,
        prd_content, # Pass the generated PRD to the technical plan function
        llm_provider
    )

    print("PRD, Historias de Usuario y Plan Técnico generados (usando LLM)...")
    return prd_content, user_stories_content, technical_plan_content


async def generate_technical_plan(conversation_history: List[Dict[str, str]], project_index, prd_content_for_tp: str, llm_provider: str = "google"):
    """
    Genera un plan de acción técnico basado en el historial de conversación, el contexto del proyecto y el PRD generado.
    Este plan incluirá detalles sobre arquitectura, componentes/ficheros afectados,
    convenciones de nombres, puntos de integración y enfoques de implementación.
    """
    print("\n--- Generando Plan Técnico ---")

    llm = _get_llm(llm_provider)

    # Combinar todo el contexto de la conversación
    full_context = ""
    for msg in conversation_history:
        if msg['role'] == 'pm':
            full_context += f"{msg['role'].upper()}: {msg['content']}\n"

    # Plantilla para el plan técnico

    technical_plan_prompt_content = _load_template_content("templates/prompts/technical_plan_prompt.txt")
    technical_plan_template = PromptTemplate(technical_plan_prompt_content)

    relevant_project_info = _get_relevant_project_info(project_index, conversation_history, "la planificación de la implementación (arquitectura, componentes, patrones)")

    # Generar el plan técnico usando el LLM
    technical_plan_content = ""
    try:
        full_prompt_text_tp = technical_plan_template.format(
            conversation_context=full_context,
            project_info=relevant_project_info,
            prd_content_for_tp=prd_content_for_tp
        )
        llm_response_tp = await llm.acomplete(full_prompt_text_tp)
        technical_plan_content = llm_response_tp.text.strip()

        if not technical_plan_content.startswith("# Plan Técnico"):
            technical_plan_content = "# Plan Técnico\n" + technical_plan_content

    except Exception as e:
        print(f"DEBUG: Error al generar Plan Técnico - Tipo: {type(e).__name__}, Mensaje: {e}")
        technical_plan_content = f"Error al generar el Plan Técnico con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."

    print("Plan Técnico generado (usando LLM)...")
    return technical_plan_content

# --- Fase 4: Chat de Desarrolladores y Resumen para Jira ---

async def get_developer_chat_response(
    developer_chat_history: List[Dict[str, str]],
    project_index,
    prd_content: str,
    user_stories_content: str,
    technical_plan_content: str,
    llm_provider: str = "google"
) -> str:
    """
    Genera una respuesta para el chat del desarrollador, usando el PRD, las Historias de Usuario,
    el Plan Técnico y el índice del proyecto como contexto.
    """
    print("\n--- Generando respuesta para el chat del desarrollador ---")

    llm = _get_llm(llm_provider)
    
    # Cargar el prompt específico para el chat del desarrollador
    developer_chat_prompt_content = _load_template_content("templates/prompts/developer_chat_prompt.txt")
    developer_chat_template = PromptTemplate(developer_chat_prompt_content)

    # Contexto relevante del proyecto (usando una consulta más específica para desarrolladores)
    relevant_project_info = _get_relevant_project_info(project_index, developer_chat_history, "responder preguntas técnicas sobre la implementación de la propuesta")

    full_prompt_text = developer_chat_template.format(
        developer_chat_context="\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in developer_chat_history]),
        prd_content=prd_content,
        user_stories_content=user_stories_content,
        technical_plan_content=technical_plan_content,
        project_info=relevant_project_info
    )

    try:
        llm_response = await llm.acomplete(full_prompt_text)
        return llm_response.text.strip()
    except Exception as e:
        print(f"DEBUG: Error al generar respuesta para el chat del desarrollador - Tipo: {type(e).__name__}, Mensaje: {e}")
        return f"Error al generar la respuesta para el chat del desarrollador con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."


async def summarize_developer_chat(
    developer_chat_history: List[Dict[str, str]],
    llm_provider: str = "google"
) -> str:
    """
    Genera un resumen conciso del chat del desarrollador para un ticket de Jira.
    """
    print("\n--- Generando resumen del chat del desarrollador para Jira ---")

    llm = _get_llm(llm_provider)

    # Cargar el prompt específico para el resumen de Jira
    jira_summary_prompt_content = _load_template_content("templates/prompts/jira_summary_prompt.txt")
    jira_summary_template = PromptTemplate(jira_summary_prompt_content)

    # Preparar el contexto del chat para el resumen
    chat_context_for_summary = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in developer_chat_history])

    full_prompt_text = jira_summary_template.format(
        developer_chat_context=chat_context_for_summary
    )

    try:
        llm_response = await llm.acomplete(full_prompt_text)
        return llm_response.text.strip()
    except Exception as e:
        print(f"DEBUG: Error al generar resumen para Jira - Tipo: {type(e).__name__}, Mensaje: {e}")
        return f"Error al generar el resumen para Jira con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."

async def generate_code_agent_brief(
    developer_chat_history: List[Dict[str, str]],
    project_index,
    prd_content: str,
    user_stories_content: str,
    technical_plan_content: str,
    llm_provider: str = "google"
) -> str:
    """
    Genera un brief detallado y optimizado para un agente de IA generador de código,
    incluyendo todo el contexto relevante para la implementación.
    """
    print("\n--- Generando brief para el agente de código ---")

    llm = _get_llm(llm_provider)

    # Cargar el prompt específico para el brief del agente de código
    code_agent_brief_prompt_content = _load_template_content("templates/prompts/code_agent_brief_prompt.txt")
    code_agent_brief_template = PromptTemplate(code_agent_brief_prompt_content)

    # Contexto relevante del proyecto (usando una consulta más específica para la implementación de código)
    relevant_project_info = _get_relevant_project_info(project_index, developer_chat_history, "generar código para la implementación")

    full_prompt_text = code_agent_brief_template.format(
        developer_chat_context="\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in developer_chat_history]),
        prd_content=prd_content,
        user_stories_content=user_stories_content,
        technical_plan_content=technical_plan_content,
        project_info=relevant_project_info
    )

    try:
        llm_response = await llm.acomplete(full_prompt_text)
        return llm_response.text.strip()
    except Exception as e:
        print(f"DEBUG: Error al generar brief para agente de código - Tipo: {type(e).__name__}, Mensaje: {e}")
        return f"Error al generar el brief para el agente de código con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."


if __name__ == "__main__":
    pass 