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


ANALYZER_PROMPT_BASE = """Eres un analizador de requerimientos para un sistema agentic.

Transforma la descripción del usuario en una especificación estructurada del dominio.

Responde SOLO con JSON válido con esta forma:
{
  "original_request": "string",
  "entities": [
    {
      "name": "singular",
      "plural_name": "plural",
      "description": "string",
      "fields": [{"name": "string", "type": "string", "required": true}],
      "operations": ["create", "list", "get", "update", "delete"]
    }
  ],
  "constraints": ["string"]
}

Reglas:
- Al menos una entidad.
- Si el usuario no define campos, infiere campos razonables.
- Usa nombres simples, sin snake_case complejo.
- Nunca devuelvas markdown.
"""

ANALYZER_USER_TEMPLATE = """Descripción del dominio:
{requirement}

Genera la especificación estructurada."""


def build_analyzer_messages(user_requirement: str) -> list[dict[str, str]]:
    user_content = ANALYZER_USER_TEMPLATE.format(requirement=user_requirement.strip())
    return [
        {"role": "system", "content": ANALYZER_PROMPT_BASE},
        {"role": "user", "content": user_content},
    ]


DESIGNER_PROMPT_BASE = """Eres un diseñador de APIs FastAPI.

Recibirás una especificación de dominio estructurada en JSON.
Debes diseñar una API CRUD mínima en un solo archivo Python.

Requisitos:
- Usar FastAPI y modelos Pydantic.
- Implementar almacenamiento en memoria.
- Incluir app = FastAPI().
- Incluir endpoints CRUD para las operaciones definidas.
- Mantener código claro y ejecutable como main.py.
- Devuelve SOLO código Python, sin markdown.
"""


def build_designer_messages(domain_spec_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": DESIGNER_PROMPT_BASE},
        {
            "role": "user",
            "content": (
                "Especificación estructurada del dominio:\n\n"
                f"{domain_spec_json}\n\n"
                "Genera el archivo completo."
            ),
        },
    ]


BACKEND_DESIGNER_PROMPT_BASE = """Eres un arquitecto backend.

Tu tarea es transformar la fuente de verdad de dominio en una especificación backend reusable.

Debes responder SOLO JSON válido con esta estructura:
{
  "source_format": "natural_language | json | basic_schema",
  "source_summary": "string",
  "entities": [
    {
      "name": "string",
      "plural_name": "string",
      "attributes": [
        {"name": "string", "type": "string", "required": true, "unique": false}
      ]
    }
  ],
  "relations": [
    {
      "source_entity": "string",
      "target_entity": "string",
      "relation_type": "one_to_one | one_to_many | many_to_many",
      "source_field": "string",
      "target_field": "string"
    }
  ],
  "crud_endpoints": [
    {
      "method": "GET|POST|PUT|DELETE",
      "path": "/resource",
      "operation": "create|list|get|update|delete",
      "entity": "EntityName",
      "relation": null
    }
  ],
  "relational_endpoints": [
    {
      "method": "GET|POST|DELETE",
      "path": "/parents/{parent_id}/children",
      "operation": "list_relation|link_relation|unlink_relation|get_relation",
      "entity": "ParentEntity",
      "relation": "Parent-Child"
    }
  ],
  "consistency_notes": ["string"]
}

Reglas:
- Debe existir al menos una entidad.
- Incluye endpoints CRUD por cada entidad.
- Si hay relaciones, incluye endpoints relacionales.
- No uses markdown.
"""


def build_backend_designer_messages(source_of_truth: str, source_format: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": BACKEND_DESIGNER_PROMPT_BASE},
        {
            "role": "user",
            "content": (
                f"Formato de entrada detectado: {source_format}\n\n"
                "Fuente de verdad:\n"
                f"{source_of_truth}\n\n"
                "Genera la especificación backend estructurada."
            ),
        },
    ]


GENERATOR_FROM_SPEC_PROMPT_BASE = """Eres un generador de APIs FastAPI.

Recibirás una especificación backend ya diseñada.
Genera un único archivo Python ejecutable con FastAPI:
- modelos Pydantic
- almacenamiento en memoria
- endpoints CRUD
- endpoints relacionales definidos
- incluir app = FastAPI()
- salida solo código Python sin markdown
"""


def build_generator_from_spec_messages(backend_spec_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": GENERATOR_FROM_SPEC_PROMPT_BASE},
        {
            "role": "user",
            "content": (
                "Especificación backend:\n\n"
                f"{backend_spec_json}\n\n"
                "Genera el archivo main.py completo."
            ),
        },
    ]
