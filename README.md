# Generador de PRDs e Historias de Usuario

Esta aplicación web es una herramienta diseñada para ayudar a los Product Managers a generar Product Requirements Documents (PRDs) e Historias de Usuario de manera eficiente. Permite interactuar con un asistente de IA para recopilar información, indexar un proyecto local para contextualizar las respuestas y generar documentos basados en plantillas predefinidas.

## Características

*   **Indexación de Proyecto Local**: Indexa directorios de proyectos (código, documentación, etc.) para que la IA tenga contexto relevante al generar PRDs e Historias de Usuario.
*   **Interacción Conversacional**: Un chat interactivo donde el asistente de IA hace preguntas aclaratorias para recopilar los detalles necesarios.
*   **Generación de Documentos**: Genera PRDs y Historias de Usuario basados en el contexto conversacional y las plantillas seleccionadas.
*   **Soporte Multi-LLM**: Permite alternar entre modelos de Google Gemini y modelos locales a través de Ollama (ej. Gemma 3n).
*   **Gestión de Plantillas**: Soporte para diferentes tipos de documentos (PRD, PRD Feature, Feature, Bug, Work) con plantillas asociadas.
*   **Funcionalidad de Drag & Drop (Parcial)**: Soporte para adjuntar archivos a través de arrastrar y soltar en el chat (con validaciones de tipo y tamaño).

## Configuración y Ejecución

Sigue estos pasos para configurar y ejecutar la aplicación en tu entorno local.

### Prerrequisitos

*   Python 3.x
*   `pip` (gestor de paquetes de Python)
*   Git (para `gitingest`)
*   Opcional: Ollama (para usar modelos locales como Gemma 3n)

### 1. Clonar el Repositorio

Si aún no lo has hecho, clona este repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd prd-creator
```

### 2. Crear y Activar un Entorno Virtual (Recomendado)

Es una buena práctica usar un entorno virtual para gestionar las dependencias del proyecto:

```bash
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux
# Para Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias de Python

Instala todas las librerías necesarias utilizando `pip`:

```bash
pip install -r requirements.txt
```

### 4. Configurar la Clave de API de Google (Opcional, para Gemini)

Si deseas utilizar los modelos de Google Gemini, necesitas una clave de API.

1.  Obtén tu clave de API de Google AI Studio.
2.  Crea un archivo `.env` en la raíz de tu proyecto (`prd-creator/`) con el siguiente contenido, reemplazando `TU_API_KEY_AQUI` con tu clave real:

    ```
    GOOGLE_API_KEY=TU_API_KEY_AQUI
    ```

### 5. Configurar Ollama (Opcional, para modelos locales)

Si deseas utilizar modelos de lenguaje grandes (LLMs) locales como Gemma 3n:

1.  **Instala Ollama**: Descarga e instala la aplicación Ollama desde [ollama.com](https://ollama.com/) para tu sistema operativo.
2.  **Descarga el Modelo**: Una vez instalado Ollama, abre tu terminal y descarga el modelo recomendado para máquinas con recursos limitados (como MacBook Air M1 con 8GB de RAM):

    ```bash
    ollama run gemma3n:e2b
    ```
    Espera a que la descarga se complete.

### 6. Ejecutar la Aplicación

Finalmente, inicia el servidor FastAPI:

```bash
uvicorn main:app --reload
```

Abre tu navegador web y visita `http://127.0.0.1:8000` (o la dirección que muestre Uvicorn) para acceder a la aplicación.

## Uso

1.  **Ruta del Proyecto Local**: Ingresa la ruta al directorio de tu proyecto local para que la IA pueda indexar tu código y obtener contexto.
2.  **Forzar Re-indexación**: Marca esta opción si deseas borrar el índice existente y volver a indexar el proyecto.
3.  **Tipo de Documento**: Selecciona el tipo de documento que deseas generar (PRD, PRD Feature, Feature, Bug, Work). Si seleccionas "PRD Feature", se habilitará un campo para que pegues un PRD existente.
4.  **Proveedor de LLM**: Elige entre "Google (Gemini)" o "Ollama (Llama3)" (que usará gemma3n:e2b).
5.  **Iniciar Conversación**: Haz clic en este botón para comenzar la interacción con la IA.
6.  **Chat con la IA**: Responde a las preguntas de la IA para proporcionar el contexto necesario. Puedes hacer clic en "Generar Documentos Ahora" en cualquier momento.
7.  **Generar Documentos**: Una vez que sientas que has proporcionado suficiente información, haz clic en "Generar Documentos Ahora" para obtener el PRD y las Historias de Usuario.
8.  **Copiar/Descargar**: Copia el contenido generado al portapapeles o descárgalo.

---
