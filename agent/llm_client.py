"""Cliente mínimo para llamar a un LLM compatible con OpenAI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - mensaje claro en runtime
    OpenAI = None  # type: ignore[misc, assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class LLMError(Exception):
    """Error al invocar el LLM o al interpretar la respuesta."""


def generate_chat_completion(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.2,
) -> str:
    """
    Envía un chat al LLM y devuelve el texto del primer choice.

    Usa variables de entorno:
    - OPENAI_API_KEY (obligatoria salvo que el cliente no la exija en tu proveedor)
    - OPENAI_BASE_URL (opcional, para APIs compatibles)
    - OPENAI_MODEL (opcional, por defecto gpt-4o-mini)
    """
    if OpenAI is None:
        raise LLMError(
            "Falta el paquete 'openai'. Instala dependencias: pip install -r requirements.txt"
        ) from _IMPORT_ERROR

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError(
            "Falta OPENAI_API_KEY: configúrala en el archivo .env (carpeta agent) "
            "o como variable de entorno del sistema."
        )

    base_url = os.getenv("OPENAI_BASE_URL") or None
    resolved_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    try:
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=resolved_model,
            messages=messages,
            temperature=temperature,
        )
    except Exception as exc:  # noqa: BLE001 - capa delgada de manejo de errores del SDK/red
        raise LLMError(f"Fallo al llamar al LLM: {exc}") from exc

    choice = response.choices[0] if response.choices else None
    content = choice.message.content if choice and choice.message else None
    if not content or not str(content).strip():
        raise LLMError("El LLM devolvió una respuesta vacía.")

    return str(content).strip()
