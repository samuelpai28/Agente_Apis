"""Flujo agentic: análisis -> diseño backend -> generación -> validación."""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.analyzer import analyze_domain
from agents.designer import design_backend_spec, validate_backend_spec_consistency
from agents.generator_agent import generate_api_code_from_spec
from generator import validate_has_fastapi_app


class AgenticState(TypedDict, total=False):
    user_requirement: str
    domain_spec: dict
    backend_spec: dict
    backend_spec_ok: bool
    backend_spec_errors: list[str]
    generated_code: str
    validation_ok: bool
    validation_error: str


def analyzer_node(state: AgenticState) -> AgenticState:
    spec = analyze_domain(state["user_requirement"])
    return {"domain_spec": spec.model_dump()}


def designer_node(state: AgenticState) -> AgenticState:
    from schemas.domain import DomainSpec

    spec = DomainSpec.model_validate(state["domain_spec"])
    backend_spec = design_backend_spec(spec)
    return {"backend_spec": backend_spec.model_dump()}


def backend_spec_validator_node(state: AgenticState) -> AgenticState:
    from schemas.backend_spec import BackendApiSpec

    backend_spec = BackendApiSpec.model_validate(state["backend_spec"])
    ok, errors = validate_backend_spec_consistency(backend_spec)
    return {"backend_spec_ok": ok, "backend_spec_errors": errors}


def generator_node(state: AgenticState) -> AgenticState:
    from schemas.backend_spec import BackendApiSpec

    backend_spec = BackendApiSpec.model_validate(state["backend_spec"])
    code = generate_api_code_from_spec(backend_spec)
    return {"generated_code": code}


def validation_node(state: AgenticState) -> AgenticState:
    if not state.get("backend_spec_ok", False):
        return {
            "validation_ok": False,
            "validation_error": (
                "La especificación backend es inconsistente: "
                + "; ".join(state.get("backend_spec_errors", []))
            ),
        }

    code = state.get("generated_code", "")
    if validate_has_fastapi_app(code):
        return {"validation_ok": True}
    return {
        "validation_ok": False,
        "validation_error": "No se encontró 'FastAPI()' en el código generado.",
    }


def build_agentic_graph():
    graph = StateGraph(AgenticState)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("designer", designer_node)
    graph.add_node("backend_spec_validator", backend_spec_validator_node)
    graph.add_node("generator", generator_node)
    graph.add_node("validator", validation_node)

    graph.set_entry_point("analyzer")
    graph.add_edge("analyzer", "designer")
    graph.add_edge("designer", "backend_spec_validator")
    graph.add_edge("backend_spec_validator", "generator")
    graph.add_edge("generator", "validator")
    graph.add_edge("validator", END)
    return graph.compile()


def run_agentic_flow(user_requirement: str) -> AgenticState:
    app = build_agentic_graph()
    return app.invoke({"user_requirement": user_requirement})

