"""Especificación de backend diseñada por el agente arquitecto."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BackendAttribute(BaseModel):
    name: str
    type: str
    required: bool = True
    unique: bool = False


class BackendEntity(BaseModel):
    name: str
    plural_name: str
    attributes: list[BackendAttribute] = Field(default_factory=list)


class BackendRelation(BaseModel):
    source_entity: str
    target_entity: str
    relation_type: str  # one_to_one, one_to_many, many_to_many
    source_field: str
    target_field: str


class BackendEndpoint(BaseModel):
    method: str
    path: str
    operation: str
    entity: str
    relation: str | None = None


class BackendApiSpec(BaseModel):
    source_format: str  # natural_language | json | basic_schema
    source_summary: str
    entities: list[BackendEntity] = Field(default_factory=list)
    relations: list[BackendRelation] = Field(default_factory=list)
    crud_endpoints: list[BackendEndpoint] = Field(default_factory=list)
    relational_endpoints: list[BackendEndpoint] = Field(default_factory=list)
    consistency_notes: list[str] = Field(default_factory=list)

