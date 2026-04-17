# Agente generador de APIs (demo)

Herramienta de línea de comandos que usa un LLM (API compatible con OpenAI) para generar una API **FastAPI** mínima con **CRUD en memoria** y la guarda en `generated_api/main.py`.

## Requisitos

- Python 3.10+
- Clave en `agent/.env` (ver abajo) o variable de entorno `OPENAI_API_KEY`
- Opcional: `OPENAI_BASE_URL` (p. ej. proveedor compatible), `OPENAI_MODEL` (por defecto `gpt-4o-mini`)

## Instalación

```bash
cd agent
pip install -r requirements.txt
```

Si aún no tienes `.env`, duplica la plantilla (PowerShell: `Copy-Item .env.example .env`; en macOS/Linux: `cp .env.example .env`).

Edita `agent/.env` y pega tu clave en `OPENAI_API_KEY=...`. Ese archivo está en `.gitignore` para no subir secretos.

## Uso

1. Generar código:

```bash
python main.py
```

Escribe algo como: `API de tareas con título y estado`.

2. Levantar la API generada (desde la carpeta `agent`):

```bash
uvicorn generated_api.main:app --reload
```

Abre la documentación interactiva en `http://127.0.0.1:8000/docs`.

## Estructura

- `main.py` — entrada por consola y flujo principal
- `llm_client.py` — llamada al modelo
- `prompts.py` — prompts reutilizables
- `generator.py` — ensambla el prompt y post-procesa la respuesta
- `file_writer.py` — escribe `generated_api/main.py`

## Notas

- El agente valida que el código contenga `FastAPI()` antes de guardarlo.
- No se incluye base de datos; la API generada usa almacenamiento en memoria.
