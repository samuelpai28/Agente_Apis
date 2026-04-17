"""Punto de entrada del agente generador de APIs."""

from __future__ import annotations

import sys

from file_writer import write_generated_api
from generator import generate_fastapi_code, validate_has_fastapi_app
from llm_client import LLMError


def main() -> int:
    print("Agente generador de APIs (FastAPI + LLM)")
    print("Describe la API que necesitas (una línea o varias). Ctrl+Z + Enter en Windows para terminar entrada multilínea.\n")

    try:
        requirement = input("> ").strip()
    except EOFError:
        requirement = ""

    if not requirement:
        print("No se ingresó ningún requerimiento. Saliendo.")
        return 1

    try:
        code = generate_fastapi_code(requirement)
    except LLMError as exc:
        print(f"Error del LLM: {exc}", file=sys.stderr)
        return 2

    if not validate_has_fastapi_app(code):
        print(
            "El código generado no pasó la validación (no se encontró 'FastAPI()'). "
            "No se guardó el archivo. Intenta de nuevo o ajusta OPENAI_MODEL.",
            file=sys.stderr,
        )
        return 3

    out_path = write_generated_api(code)
    print(f"\nAPI generada correctamente en: {out_path}")
    print("Ejecuta la API con:")
    print("  uvicorn generated_api.main:app --reload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
