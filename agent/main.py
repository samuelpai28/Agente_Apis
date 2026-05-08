"""Punto de entrada del agente generador de APIs."""

from __future__ import annotations

import sys

from file_writer import write_generated_api
from workflows.agentic_flow import run_agentic_flow
from llm_client import LLMError


def main() -> int:
    print("Agente generador de APIs (arquitectura agentic + LangGraph)")
    print("Describe la API que necesitas (una línea o varias). Ctrl+Z + Enter en Windows para terminar entrada multilínea.\n")

    try:
        requirement = input("> ").strip()
    except EOFError:
        requirement = ""

    if not requirement:
        print("No se ingresó ningún requerimiento. Saliendo.")
        return 1

    try:
        result = run_agentic_flow(requirement)
    except LLMError as exc:
        print(f"Error del LLM: {exc}", file=sys.stderr)
        return 2

    if not result.get("validation_ok"):
        print(
            "El código generado no pasó la validación (no se encontró 'FastAPI()'). "
            "No se guardó el archivo. Intenta de nuevo o ajusta OPENAI_MODEL.",
            file=sys.stderr,
        )
        return 3

    code = str(result.get("generated_code", "")).strip()
    if not code:
        print("No se obtuvo código desde el flujo agentic.", file=sys.stderr)
        return 4

    out_path = write_generated_api(code)
    domain_spec = result.get("domain_spec", {})
    entities = domain_spec.get("entities", []) if isinstance(domain_spec, dict) else []
    backend_spec = result.get("backend_spec", {})
    backend_entities = backend_spec.get("entities", []) if isinstance(backend_spec, dict) else []
    backend_relations = backend_spec.get("relations", []) if isinstance(backend_spec, dict) else []

    print(f"\nAPI generada correctamente en: {out_path}")
    if entities:
        print(f"Entidades detectadas por el agente analizador: {len(entities)}")
    if backend_entities:
        print(f"Entidades diseñadas para backend: {len(backend_entities)}")
    if backend_relations:
        print(f"Relaciones de dominio detectadas: {len(backend_relations)}")
    print("Ejecuta la API con:")
    print("  uvicorn generated_api.main:app --reload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
