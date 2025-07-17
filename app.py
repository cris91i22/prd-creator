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
                return index
        except Exception as e:
            print(f"No se pudo cargar el índice existente o la colección no existe (error: {e}). Procediendo con la indexación.")
            # Si hay un error al cargar, procederemos a re-indexar.

    print("Creando o re-indexando el proyecto...")
    # Paso 1: Ejecutar gitingest
    try:
        print(f"Procesando el proyecto con gitingest: {project_path}")
        summary, tree, gitingest_content = await ingest_async(project_path)
        print("gitingest completado. Contenido extraído.")
    except Exception as e:
        print(f"Error al ejecutar gitingest: {e}")
        gitingest_content = "Este es un contenido de fallback porque gitingest falló o no se pudo ejecutar. Asegúrate de que el directorio del proyecto exista y sea válido."
    
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
    return index

# --- Fase 2: Descripción de Funcionalidad e Interacción Conversacional ---

async def get_next_chat_question(conversation_history: List[Dict[str, str]], project_index, template_type: str, existing_prd_content: Optional[str] = None, llm_provider: str = "google"):
    """
    Genera la siguiente pregunta para el PM basada en el historial de conversación
    y el contexto del proyecto, utilizando un LLM.
    """
    from llama_index.llms.google_genai import GoogleGenAI
    from llama_index.core.prompts import PromptTemplate
    from llama_index.llms.ollama import Ollama # Added for Ollama

    llm = None
    if llm_provider == "google":
        llm = GoogleGenAI(model="models/gemini-2.5-flash", max_output_tokens=8000)
    elif llm_provider == "ollama":
        # Default to llama3, user can change this
        llm = Ollama(model="gemma3n:e2b", request_timeout=360.0) # Changed from llama3 to gemma3n:e2b
    else:
        raise ValueError("Invalid LLM provider specified.")


    base_prompt = """Eres un asistente de IA que ayuda a los Product Managers a recopilar información para PRDs e Historias de Usuario.
        Basado en el siguiente historial de conversación y el contexto del proyecto indexado, formula una pregunta de clarificación para el PM.
        La pregunta debe ser concisa, relevante y ayudar a recopilar detalles esenciales para un PRD/Historia de Usuario completo.

        Historial de Conversación:
        {conversation_context}

        Información Relevante del Proyecto (si aplica):
        {project_info}
        """

    if not conversation_history or (len(conversation_history) == 1 and conversation_history[0].get("role") == "pm"):
        # Si es el inicio de la conversación o solo el primer mensaje del PM
        if template_type == 'prd_feature_existing':
            base_prompt += f"""
            El PM ha proporcionado el siguiente contenido de PRD existente:
            {existing_prd_content}
            Tu objetivo es ayudar a desglosar este PRD en Historias de Usuario detalladas.
            Para empezar, ¿en qué funcionalidades o secciones del PRD existente deberíamos enfocarnos para generar las Historias de Usuario?
            """
        elif template_type == 'prd.md' or template_type == 'feature.md':
            base_prompt += """
            Para empezar, ¿cuál es el problema principal que esta funcionalidad busca resolver para el usuario, o cuál es el objetivo principal que queremos lograr con esta nueva característica?
            """
        else:
            # Default for other templates if needed
            base_prompt += """
            Para empezar, ¿cuál es el problema o el objetivo principal de lo que estamos discutiendo?
            """
    else:
        if template_type == 'prd_feature_existing':
            # Adaptar el prompt para el caso de PRD Feature
            base_prompt += f"""
            El PM ha proporcionado el siguiente contenido de PRD existente:
            {existing_prd_content}
            Tu objetivo es ayudar a desglosar este PRD en Historias de Usuario detalladas.
            """
        elif template_type == 'prd.md':
            base_prompt += """
            Tu objetivo es recopilar suficiente información para generar un PRD completamente nuevo.
            """
        elif template_type == 'feature.md': # This is the default behavior.
            base_prompt += """
            Tu objetivo es recopilar suficiente información para generar un PRD y Historias de Usuario para una nueva funcionalidad.
            """
        # Add other template type specific instructions here if needed

    base_prompt += """
        Siguiente pregunta para el PM:
        """

    prompt_template = PromptTemplate(base_prompt)

    relevant_project_info = "No se recuperó información específica del proyecto para el contexto de la pregunta."
    if project_index:
        try:
            query_engine = project_index.as_query_engine()
            # Usar una consulta más general para las preguntas del chat
            simulated_query = f"Dadas las funcionalidades mencionadas en la conversación, ¿qué información técnica relevante del proyecto podría necesitar para formular la siguiente pregunta al PM?"
            response = query_engine.query(simulated_query)
            if response and response.response:
                relevant_project_info = response.response
            else:
                relevant_project_info = "No se encontró información relevante del proyecto para esta consulta específica."
        except Exception as e:
            relevant_project_info = f"Error al recuperar información del proyecto para la pregunta: {str(e)}"

    full_prompt_text = prompt_template.format(
        conversation_context="\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history]),
        project_info=relevant_project_info
    )

    try:
        llm_response = await llm.acomplete(full_prompt_text)
        return llm_response.text.strip()
    except Exception as e:
        return f"Error al generar la pregunta con el LLM: {str(e)}. Por favor, verifica tu clave de API y la disponibilidad del modelo."


# --- Fase 3: Generación de PRDs e Historias de Usuario ---

async def generate_prd_and_user_stories(conversation_history: List[Dict[str, str]], project_index, template_type: str, existing_prd_content: Optional[str] = None, llm_provider: str = "google"):
    """
    Genera el PRD y las historias de usuario.
    En una aplicación real, aquí se usaría un LLM (ej. Gemini-Pro)
    con todo el contexto y posiblemente plantillas.
    """
    print("\n--- Generando PRD e Historias de Usuario ---")

    # Cargar el contenido del template seleccionado
    template_file_path = os.path.join("templates", template_type)
    template_content = ""
    try:
        # For prd_feature_existing, we don't load from a file, but use the provided content
        if template_type == 'prd_feature_existing':
            template_content = existing_prd_content if existing_prd_content else ""
            print("Usando contenido de PRD existente para generación.")
        else:
            with open(template_file_path, 'r') as f:
                template_content = f.read()
            print(f"Template '{template_type}' cargado con éxito.")
    except FileNotFoundError:
        print(f"Error: El template '{template_type}' no fue encontrado.")
        template_content = ""
    except Exception as e:
        print(f"Error al leer el template '{template_type}': {e}")
        template_content = ""

    # Combinar todo el contexto para el LLM
    full_context = ""
    for msg in conversation_history:
        if msg['role'] == 'pm': # Only include messages from the Product Manager
            full_context += f"{msg['role'].upper()}: {msg['content']}\n"

    # Simulación de la generación del PRD y HU
    # Utilizaremos un LLM real para la generación
    from llama_index.llms.google_genai import GoogleGenAI
    from llama_index.core.prompts import PromptTemplate
    from llama_index.llms.ollama import Ollama # Added for Ollama

    llm = None
    if llm_provider == "google":
        llm = GoogleGenAI(model="models/gemini-2.5-flash", max_output_tokens=8000)
    elif llm_provider == "ollama":
        llm = Ollama(model="gemma3n:e2b", request_timeout=360.0) # Changed from llama3 to gemma3n:e2b
    else:
        raise ValueError("Invalid LLM provider specified.")

    # Plantilla para el PRD
    prd_template = PromptTemplate(
        """Genera un Product Requirements Document (PRD) EXTREMADAMENTE CONCISO y detallado, basado en el siguiente contexto de conversación con el PM y la información del proyecto indexada. El PRD debe ser completo pero ABSOLUTAMENTE DIRECTO, cubriendo todos los puntos clave con la menor cantidad de palabras posible. Cada sección debe ser muy breve.
        Utiliza el siguiente template para guiar la estructura del documento. 
        IMPORTANTE: Genera ÚNICAMENTE el contenido del PRD. No incluyas ningún saludo, introducción conversacional, o resumen de la conversación. Céntrate exclusivamente en el documento final.

        --- INICIO DEL TEMPLATE ---
        {template_content}
        --- FIN DEL TEMPLATE ---

        Contexto de Conversación con el PM:
        {conversation_context}

        Información Relevante del Proyecto (si aplica):
        {project_info}
        """
    )

    # Plantilla para las Historias de Usuario
    user_stories_template = PromptTemplate(
        """Genera un conjunto MUY CONCISO Y CLARO de Historias de Usuario basadas en el siguiente contexto de conversación con el PM y el PRD generado. Las Historias de Usuario deben seguir el formato 'Como [rol], quiero [funcionalidad], para [beneficio]'. Cada historia debe ser una sola frase directa y accionable.
        IMPORTANTE: Genera ÚNICAMENTE las Historias de Usuario. No incluyas ningún saludo, introducción conversacional, o resumen de la conversación. Céntrate exclusivamente en las historias.

        PRD Generado:
        {prd_content_for_us}

        Contexto de Conversación con el PM:
        {conversation_context}

        Información Relevante del Proyecto (si aplica):
        {project_info}
        """
    )

    # Simular la recuperación de información relevante del proyecto
    relevant_project_info = "No se recuperó información específica del proyecto para la simulación de generación."
    if project_index:
        try:
            query_engine = project_index.as_query_engine()
            # Usar una consulta más general para las preguntas del chat
            simulated_query = f"Basado en la conversación sobre la funcionalidad de {conversation_history[0].get('content', 'una nueva característica')}, ¿cuál es la información técnica más concisa y relevante del proyecto para la implementación?"
            response = query_engine.query(simulated_query)
            if response and response.response:
                relevant_project_info = response.response
            else:
                relevant_project_info = "No se encontró información relevante del proyecto para esta consulta específica."
        except Exception as e:
            relevant_project_info = f"Error al recuperar información del proyecto: {str(e)}"

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

    from llama_index.llms.google_genai import GoogleGenAI
    from llama_index.core.prompts import PromptTemplate
    from llama_index.llms.ollama import Ollama

    llm = None
    if llm_provider == "google":
        llm = GoogleGenAI(model="models/gemini-2.5-flash", max_output_tokens=8000)
    elif llm_provider == "ollama":
        llm = Ollama(model="gemma3n:e2b", request_timeout=360.0)
    else:
        raise ValueError("Invalid LLM provider specified.")

    # Combinar todo el contexto de la conversación
    full_context = ""
    for msg in conversation_history:
        if msg['role'] == 'pm':
            full_context += f"{msg['role'].upper()}: {msg['content']}\n"

    # Plantilla para el plan técnico
    technical_plan_template = PromptTemplate(
        """Eres un asistente de IA que ayuda a los Product Managers a recopilar información para PRDs e Historias de Usuario, y también a generar planes técnicos de alto nivel.
        Basado en el siguiente contexto de conversación con el PM y la información del proyecto indexada, genera un plan de acción técnico EXTREMADAMENTE CONCISO y directo.
        El plan debe cubrir los siguientes puntos clave con la menor cantidad de palabras posible, utilizando un formato claro y listado.

        El plan debe incluir:
        - Cómo esta funcionalidad encaja en la arquitectura existente.
        - Qué archivos o componentes existentes podrían verse afectados.
        - Convenciones de nombres a seguir basadas en la base de código actual.
        - Puntos de integración con funcionalidades existentes.
        - Enfoque de implementación sugerido basado en patrones actuales.
        - **Consideraciones Adicionales**: Menciona brevemente (1-2 frases por punto):
            - Manejo de errores y casos límite relevantes para la funcionalidad.
            - Implicaciones de rendimiento y experiencia de usuario (UX).
            - Aspectos de seguridad.
            - Estrategia de pruebas (ej. unitarias, integración, E2E).

        IMPORTANTE: Genera ÚNICAMENTE el contenido del plan técnico. No incluyas ningún saludo, introducción conversacional, o resumen de la conversación. Céntrate exclusivamente en el plan final.

        PRD Generado:
        {prd_content_for_tp}

        Contexto de Conversación con el PM:
        {conversation_context}

        Información Relevante del Proyecto (si aplica):
        {project_info}
        """
    )

    relevant_project_info = "No se recuperó información específica del proyecto para la generación del plan técnico."
    if project_index:
        try:
            query_engine = project_index.as_query_engine()
            # Usar una consulta más general para el plan técnico
            simulated_query = f"Basado en la conversación sobre la funcionalidad de {conversation_history[0].get('content', 'una nueva característica')}, ¿cuál es la información técnica más concisa y relevante del proyecto para la planificación de la implementación (arquitectura, componentes, patrones)?"
            response = query_engine.query(simulated_query)
            if response and response.response:
                relevant_project_info = response.response
            else:
                relevant_project_info = "No se encontró información relevante del proyecto para esta consulta específica."
        except Exception as e:
            relevant_project_info = f"Error al recuperar información del proyecto para el plan técnico: {str(e)}"

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


if __name__ == "__main__":
    pass 