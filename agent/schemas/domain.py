"""Representación estructurada del dominio de entrada."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DomainField(BaseModel):
    name: str
    type: str
    required: bool = True


class DomainEntity(BaseModel):
    name: str
    plural_name: str
    description: str
    fields: list[DomainField] = Field(default_factory=list)
    operations: list[str] = Field(default_factory=list)


class DomainSpec(BaseModel):
    original_request: str
    entities: list[DomainEntity] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

