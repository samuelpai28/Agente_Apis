"""Agente analizador: texto libre -> DomainSpec."""

from __future__ import annotations

import json
import re

from llm_client import LLMError, generate_chat_completion
from prompts import build_analyzer_messages
from schemas.domain import DomainEntity, DomainField, DomainSpec


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _fallback_domain_spec(user_requirement: str) -> DomainSpec:
    base_entity = DomainEntity(
        name="Item",
        plural_name="Items",
        description="Entidad inferida automáticamente desde el requerimiento.",
        fields=[
            DomainField(name="id", type="int", required=True),
            DomainField(name="name", type="str", required=True),
            DomainField(name="description", type="str", required=False),
        ],
        operations=["create", "list", "get", "update", "delete"],
    )
    return DomainSpec(
        original_request=user_requirement,
        entities=[base_entity],
        constraints=["Especificación inferida por fallback local."],
    )


def _build_from_json_payload(payload: dict, original: str) -> DomainSpec:
    entities_raw = payload.get("entities", [])
    entities: list[DomainEntity] = []
    for entity in entities_raw:
        fields = [
            DomainField(
                name=str(field.get("name", "field")),
                type=str(field.get("type", "str")),
                required=bool(field.get("required", True)),
            )
            for field in entity.get("fields", [])
        ]
        entities.append(
            DomainEntity(
                name=str(entity.get("name", "Entity")),
                plural_name=str(entity.get("plural_name", f"{entity.get('name', 'Entity')}s")),
                description=str(entity.get("description", "")),
                fields=fields,
                operations=list(entity.get("operations", ["create", "list", "get", "update", "delete"])),
            )
        )
    return DomainSpec(
        original_request=original,
        entities=entities,
        constraints=[str(item) for item in payload.get("constraints", [])],
    )


def _build_from_basic_schema(requirement: str) -> DomainSpec | None:
    lines = [line.strip() for line in requirement.splitlines() if line.strip()]
    entity_line = next((line for line in lines if line.lower().startswith("entidad:")), None)
    attrs_line = next((line for line in lines if line.lower().startswith("atributos:")), None)
    if not entity_line:
        return None

    name = entity_line.split(":", 1)[1].strip() or "Entity"
    fields: list[DomainField] = []
    if attrs_line:
        attributes_part = attrs_line.split(":", 1)[1]
        for raw_attr in attributes_part.split(","):
            attr = raw_attr.strip()
            if not attr:
                continue
            if ":" in attr:
                attr_name, attr_type = [part.strip() for part in attr.split(":", 1)]
            else:
                attr_name, attr_type = attr, "str"
            fields.append(DomainField(name=attr_name, type=attr_type, required=True))
    if not fields:
        fields = [DomainField(name="id", type="int", required=True), DomainField(name="name", type="str", required=True)]

    return DomainSpec(
        original_request=requirement,
        entities=[
            DomainEntity(
                name=name,
                plural_name=f"{name}s",
                description="Entidad creada desde esquema básico.",
                fields=fields,
                operations=["create", "list", "get", "update", "delete"],
            )
        ],
        constraints=[],
    )


def analyze_domain(user_requirement: str) -> DomainSpec:
    stripped = user_requirement.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                return _build_from_json_payload(parsed, user_requirement)
        except json.JSONDecodeError:
            pass

    basic_spec = _build_from_basic_schema(user_requirement)
    if basic_spec:
        return basic_spec

    messages = build_analyzer_messages(user_requirement)
    try:
        raw = generate_chat_completion(messages, temperature=0.1)
        parsed = json.loads(_strip_code_fences(raw))
        return DomainSpec.model_validate(parsed)
    except (LLMError, json.JSONDecodeError, ValueError):
        return _fallback_domain_spec(user_requirement)

