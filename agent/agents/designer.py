"""Agente diseñador: fuente de verdad -> BackendApiSpec."""

from __future__ import annotations

import json
import re

from llm_client import generate_chat_completion
from prompts import build_backend_designer_messages
from schemas.backend_spec import (
    BackendApiSpec,
    BackendAttribute,
    BackendEndpoint,
    BackendEntity,
    BackendRelation,
)
from schemas.domain import DomainSpec


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n", t, re.IGNORECASE)
    if fence:
        t = t[fence.end() :]
    if t.endswith("```"):
        t = t[:-3].rstrip()
    return t.strip()


def _detect_source_format(source_of_truth: str) -> str:
    stripped = source_of_truth.strip()
    if not stripped:
        return "natural_language"
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    if "entidad:" in stripped.lower() or "atributos:" in stripped.lower():
        return "basic_schema"
    return "natural_language"


def _fallback_backend_spec(source_text: str, source_format: str) -> BackendApiSpec:
    item = BackendEntity(
        name="Item",
        plural_name="Items",
        attributes=[
            BackendAttribute(name="id", type="int", required=True, unique=True),
            BackendAttribute(name="name", type="str", required=True),
            BackendAttribute(name="description", type="str", required=False),
        ],
    )
    crud = [
        BackendEndpoint(method="POST", path="/items/", operation="create", entity="Item"),
        BackendEndpoint(method="GET", path="/items/", operation="list", entity="Item"),
        BackendEndpoint(method="GET", path="/items/{item_id}", operation="get", entity="Item"),
        BackendEndpoint(method="PUT", path="/items/{item_id}", operation="update", entity="Item"),
        BackendEndpoint(method="DELETE", path="/items/{item_id}", operation="delete", entity="Item"),
    ]
    return BackendApiSpec(
        source_format=source_format,
        source_summary=source_text[:220],
        entities=[item],
        relations=[],
        crud_endpoints=crud,
        relational_endpoints=[],
        consistency_notes=["Especificación fallback usada por respuesta inválida del diseñador."],
    )


def _prepare_source(domain_spec: DomainSpec | dict | str) -> tuple[str, str]:
    if isinstance(domain_spec, DomainSpec):
        source = domain_spec.model_dump_json(indent=2)
        return source, "json"
    if isinstance(domain_spec, dict):
        source = json.dumps(domain_spec, indent=2, ensure_ascii=False)
        return source, "json"
    source = str(domain_spec)
    return source, _detect_source_format(source)


def design_backend_spec(domain_spec: DomainSpec | dict | str) -> BackendApiSpec:
    source_of_truth, source_format = _prepare_source(domain_spec)
    messages = build_backend_designer_messages(source_of_truth, source_format)
    try:
        raw = generate_chat_completion(messages, temperature=0.1)
        parsed = json.loads(_strip_code_fences(raw))
        return BackendApiSpec.model_validate(parsed)
    except Exception:
        return _fallback_backend_spec(source_of_truth, source_format)


def validate_backend_spec_consistency(spec: BackendApiSpec) -> tuple[bool, list[str]]:
    errors: list[str] = []
    entity_names = {entity.name for entity in spec.entities}
    if not entity_names:
        errors.append("No hay entidades definidas.")

    for relation in spec.relations:
        if relation.source_entity not in entity_names:
            errors.append(f"Relación con source_entity inexistente: {relation.source_entity}")
        if relation.target_entity not in entity_names:
            errors.append(f"Relación con target_entity inexistente: {relation.target_entity}")
        if relation.relation_type not in {"one_to_one", "one_to_many", "many_to_many"}:
            errors.append(f"relation_type inválido: {relation.relation_type}")

    for endpoint in spec.crud_endpoints:
        if endpoint.entity not in entity_names:
            errors.append(f"Endpoint CRUD con entidad inexistente: {endpoint.path}")

    for endpoint in spec.relational_endpoints:
        if endpoint.entity not in entity_names:
            errors.append(f"Endpoint relacional con entidad inexistente: {endpoint.path}")

    return (len(errors) == 0, errors)

