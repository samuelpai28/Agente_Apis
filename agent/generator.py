"""Orquesta el prompt y la llamada al LLM para obtener código de la API."""

from __future__ import annotations

import re

from llm_client import LLMError, generate_chat_completion
from prompts import build_generation_messages


def _strip_code_fences(text: str) -> str:
    """Elimina cercas ```python ... ``` si el modelo las incluye."""
    t = text.strip()
    fence = re.match(r"^```(?:python)?\s*\n", t, re.IGNORECASE)
    if fence:
        t = t[fence.end() :]
    if t.endswith("```"):
        t = t[: -3].rstrip()
    return t.strip()


def generate_fastapi_code(user_requirement: str) -> str:
    messages = build_generation_messages(user_requirement)
    raw = generate_chat_completion(messages)
    return _strip_code_fences(raw)


def validate_has_fastapi_app(code: str) -> bool:
    """Validación mínima: debe instanciar FastAPI()."""
    return "FastAPI()" in code
