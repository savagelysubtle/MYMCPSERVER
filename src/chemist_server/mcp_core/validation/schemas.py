"""JSON Schema definitions for tool validation."""

from typing import Any

from pydantic import BaseModel, Field

from ..errors import ValidationError
from ..logger import logger


class ParameterSchema(BaseModel):
    """Schema for a tool parameter."""

    name: str
    type: str
    description: str
    required: bool = False
    default: Any | None = None
    enum: list[Any] | None = None
    pattern: str | None = None
    min_value: float | None = None
    max_value: float | None = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format.

        Returns:
            Dict[str, Any]: JSON Schema for this parameter
        """
        schema: dict[str, Any] = {"type": self.type, "description": self.description}

        if self.default is not None:
            schema["default"] = self.default

        if self.enum:
            schema["enum"] = self.enum

        if self.pattern and self.type == "string":
            schema["pattern"] = self.pattern

        if self.min_value is not None:
            if self.type == "string":
                schema["minLength"] = int(self.min_value)
            elif self.type in ["number", "integer"]:
                schema["minimum"] = self.min_value
            elif self.type == "array":
                schema["minItems"] = int(self.min_value)

        if self.max_value is not None:
            if self.type == "string":
                schema["maxLength"] = int(self.max_value)
            elif self.type in ["number", "integer"]:
                schema["maximum"] = self.max_value
            elif self.type == "array":
                schema["maxItems"] = int(self.max_value)

        return schema


class ToolSchema(BaseModel):
    """Schema definition for a tool."""

    name: str
    version: str
    description: str
    parameters: list[ParameterSchema]
    required_parameters: list[str] = Field(default_factory=list)

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format.

        Returns:
            dict[str, Any]: JSON Schema for this tool
        """
        properties = {}
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()

        return {
            "type": "object",
            "title": f"{self.name} v{self.version}",
            "description": self.description,
            "properties": properties,
            "required": self.required_parameters,
        }


# Registry for tool schemas
_tool_schemas: dict[str, dict[str, ToolSchema]] = {}


def register_tool_schema(schema: ToolSchema) -> None:
    """Register a tool schema.

    Args:
        schema: Tool schema to register

    Raises:
        ValidationError: If schema is already registered
    """
    if schema.name not in _tool_schemas:
        _tool_schemas[schema.name] = {}

    if schema.version in _tool_schemas[schema.name]:
        raise ValidationError(
            f"Schema for tool {schema.name} version {schema.version} already registered"
        )

    _tool_schemas[schema.name][schema.version] = schema
    logger.info(
        f"Registered schema for tool {schema.name} version {schema.version}",
        tool=schema.name,
        version=schema.version,
    )


def get_tool_schema(name: str, version: str | None = None) -> ToolSchema:
    """Get a tool schema.

    Args:
        name: Tool name
        version: Tool version (latest if None)

    Returns:
        ToolSchema: Tool schema

    Raises:
        ValidationError: If schema not found
    """
    if name not in _tool_schemas:
        raise ValidationError(f"No schema registered for tool {name}")

    if version is None:
        # Get latest version
        version = max(_tool_schemas[name].keys())

    if version not in _tool_schemas[name]:
        raise ValidationError(f"No schema registered for tool {name} version {version}")

    return _tool_schemas[name][version]


def list_tool_schemas() -> dict[str, list[str]]:
    """List all registered tool schemas.

    Returns:
        dict[str, list[str]]: Map of tool names to lists of versions
    """
    return {name: list(versions.keys()) for name, versions in _tool_schemas.items()}
