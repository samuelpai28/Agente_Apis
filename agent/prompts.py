"""Prompts del agente generador de APIs (separados del código de orquestación)."""

PROMPT_BASE = """Eres un generador de APIs mínimas en Python.

TAREA: A partir de la descripción del usuario, genera UN SOLO archivo Python completo y ejecutable
que implemente una API REST con FastAPI.

REQUISITOS OBLIGATORIOS DEL CÓDIGO:
- Usar FastAPI, Pydantic y uvicorn (comentario al final con cómo ejecutar).
- Definir modelos Pydantic para los recursos (al menos un modelo principal con campos razonables).
- Almacenamiento en memoria: una lista o dict en Python (sin base de datos).
- Endpoints CRUD típicos: crear, listar, obtener por id, actualizar, eliminar.
- IDs enteros autoincrementales o UUIDs simples; consistencia en toda la API.
- Incluir `app = FastAPI()` (o equivalente asignando FastAPI() a una variable `app`).
- CORS opcional con CORSMiddleware si ayuda a pruebas locales.
- Docstrings breves en endpoints.
- Código claro, sin sobreingeniería, sin archivos adicionales ni imports relativos raros.

SALIDA:
- Devuelve ÚNICAMENTE el código Python del archivo, sin markdown, sin explicaciones antes o después.
- El código debe poder guardarse como main.py y ejecutarse con: uvicorn main:app --reload
"""

USER_REQUIREMENT_TEMPLATE = """Descripción del usuario (requerimiento de la API):

{requirement}

Genera ahora el archivo completo."""


def build_generation_messages(user_requirement: str) -> list[dict[str, str]]:
    """Construye los mensajes para el chat del LLM."""
    user_content = USER_REQUIREMENT_TEMPLATE.format(requirement=user_requirement.strip())
    return [
        {"role": "system", "content": PROMPT_BASE},
        {"role": "user", "content": user_content},
    ]
