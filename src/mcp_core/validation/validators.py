"""Validation functions for MCP Core."""

from typing import Any, Dict, Optional

import jsonschema

from ..errors import ValidationError
from ..logger import logger
from ..models.request import CoreRequest
from .schemas import get_tool_schema


def validate_request(request: CoreRequest) -> None:
    """Validate a request.

    Args:
        request: Request to validate

    Raises:
        ValidationError: If validation fails
    """
    # Validate basic request structure
    if not request.tool_name:
        raise ValidationError("Tool name is required")

    # Validate tool parameters against schema if available
    try:
        validate_tool_parameters(request.tool_name, request.parameters, request.version)
    except ValidationError as e:
        logger.warning(
            f"Validation failed for tool {request.tool_name}",
            tool=request.tool_name,
            correlation_id=request.context.correlation_id,
            error=str(e),
        )
        raise


def validate_tool_parameters(
    tool_name: str, parameters: Dict[str, Any], version: Optional[str] = None
) -> None:
    """Validate tool parameters against schema.

    Args:
        tool_name: Tool name
        parameters: Parameters to validate
        version: Tool version (latest if None)

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Get tool schema
        schema = get_tool_schema(tool_name, version)
        json_schema = schema.to_json_schema()

        # Validate against JSON Schema
        try:
            jsonschema.validate(instance=parameters, schema=json_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValidationError(
                f"Parameter validation failed: {e.message}",
                details={
                    "path": list(e.path),
                    "validator": e.validator,
                    "validator_value": e.validator_value,
                },
            ) from e
    except ValidationError as e:
        if "No schema registered" in str(e):
            # No schema available, just log and continue
            logger.warning(
                f"No schema available for tool {tool_name}, skipping validation",
                tool=tool_name,
                version=version,
            )
            return

        # Re-raise other validation errors
        raise
