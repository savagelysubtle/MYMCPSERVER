"""AIChemist tool implementation for MCP."""

from __future__ import annotations

import json
import logging
from typing import Any

try:
    from mcp import ToolContext, ToolResponse, tool
except ImportError:
    print("MCP SDK not installed. Please install it using 'pip install mcp-sdk'")

    # Create stub classes/functions for development without the SDK
    class ToolContext:
        pass

    class ToolResponse:
        def __init__(self, content=None, error=None):
            self.content = content
            self.error = error

    def tool(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger("mcp.tools.aichemist")


class Molecule(BaseModel):
    """Represents a molecule."""

    name: str = Field(..., description="Name of the molecule")
    formula: str = Field(..., description="Chemical formula")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Molecular properties"
    )


class AIChemistTool:
    """Tool for molecular modeling and simulation."""

    def __init__(self):
        """Initialize the AIChemist tool."""
        self.molecules = {}
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample molecular data."""
        sample_molecules = [
            Molecule(
                name="Water",
                formula="H2O",
                properties={
                    "molecular_weight": 18.01528,
                    "boiling_point": 100.0,
                    "melting_point": 0.0,
                    "density": 1.0,
                },
            ),
            Molecule(
                name="Carbon Dioxide",
                formula="CO2",
                properties={
                    "molecular_weight": 44.01,
                    "boiling_point": -78.5,
                    "melting_point": -56.6,
                    "density": 1.977,
                },
            ),
            Molecule(
                name="Methane",
                formula="CH4",
                properties={
                    "molecular_weight": 16.04,
                    "boiling_point": -161.5,
                    "melting_point": -182.5,
                    "density": 0.657,
                },
            ),
        ]

        for molecule in sample_molecules:
            self.molecules[molecule.name.lower()] = molecule

        logger.info(f"Loaded {len(self.molecules)} sample molecules")


# Create singleton instance
aichemist_instance = AIChemistTool()


@tool(
    name="aichemist.get_molecule",
    description="Get information about a specific molecule",
    schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the molecule to retrieve",
            }
        },
        "required": ["name"],
    },
)
async def aichemist_get_molecule(context: ToolContext, name: str) -> ToolResponse:
    """Get information about a specific molecule."""
    try:
        name_lower = name.lower()
        if name_lower in aichemist_instance.molecules:
            molecule = aichemist_instance.molecules[name_lower]
            return ToolResponse(
                content=[
                    {
                        "type": "text",
                        "text": json.dumps(molecule.model_dump(), indent=2),
                    }
                ]
            )
        else:
            return ToolResponse(
                content=[{"type": "text", "text": f"Molecule '{name}' not found."}]
            )
    except Exception as e:
        logger.error(f"Error getting molecule: {e}")
        return ToolResponse(error=str(e))


@tool(
    name="aichemist.list_molecules",
    description="List all available molecules",
    schema={
        "type": "object",
        "properties": {},
    },
)
async def aichemist_list_molecules(context: ToolContext) -> ToolResponse:
    """List all available molecules."""
    try:
        molecules = [
            {"name": mol.name, "formula": mol.formula}
            for mol in aichemist_instance.molecules.values()
        ]
        return ToolResponse(
            content=[{"type": "text", "text": json.dumps(molecules, indent=2)}]
        )
    except Exception as e:
        logger.error(f"Error listing molecules: {e}")
        return ToolResponse(error=str(e))


@tool(
    name="aichemist.calculate_property",
    description="Calculate a property for a given molecule",
    schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the molecule",
            },
            "property": {
                "type": "string",
                "description": "Property to calculate",
                "enum": [
                    "molecular_weight",
                    "boiling_point",
                    "melting_point",
                    "density",
                ],
            },
        },
        "required": ["name", "property"],
    },
)
async def aichemist_calculate_property(
    context: ToolContext, name: str, property: str
) -> ToolResponse:
    """Calculate a property for a given molecule."""
    try:
        name_lower = name.lower()
        if name_lower in aichemist_instance.molecules:
            molecule = aichemist_instance.molecules[name_lower]
            if property in molecule.properties:
                value = molecule.properties[property]
                return ToolResponse(
                    content=[
                        {
                            "type": "text",
                            "text": f"The {property} of {molecule.name} ({molecule.formula}) is {value}",
                        }
                    ]
                )
            else:
                return ToolResponse(
                    content=[
                        {
                            "type": "text",
                            "text": f"Property '{property}' not available for {molecule.name}",
                        }
                    ]
                )
        else:
            return ToolResponse(
                content=[{"type": "text", "text": f"Molecule '{name}' not found."}]
            )
    except Exception as e:
        logger.error(f"Error calculating property: {e}")
        return ToolResponse(error=str(e))
