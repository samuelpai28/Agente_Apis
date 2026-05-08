"""Agente generador: BackendApiSpec -> código FastAPI."""

from __future__ import annotations

import re

from llm_client import generate_chat_completion
from prompts import build_generator_from_spec_messages
from schemas.backend_spec import BackendApiSpec


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    fence = re.match(r"^```(?:python)?\s*\n", t, re.IGNORECASE)
    if fence:
        t = t[fence.end() :]
    if t.endswith("```"):
        t = t[:-3].rstrip()
    return t.strip()


def generate_api_code_from_spec(backend_spec: BackendApiSpec) -> str:
    messages = build_generator_from_spec_messages(backend_spec.model_dump_json(indent=2))
    raw = generate_chat_completion(messages, temperature=0.2)
    return _strip_code_fences(raw)

