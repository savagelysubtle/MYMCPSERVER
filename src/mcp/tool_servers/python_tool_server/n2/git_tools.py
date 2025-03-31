import asyncio
import logging
import sys

# Import prompt definitions
from prompts.code_prompts import code_review_prompt

# Import resource definitions
from resources.memory_resources import get_memory_bank_context

# Import utilities
from utils.logging_utils import setup_logging

from mcp.server import Server, handle_http, handle_stdio
from tools.architecture_tools import (
    generate_architecture_diagram,
    generate_class_diagram,
    map_component_structure,
)
from tools.codebase_tools import analyze_codebase_architecture, search_codebase

# Import tool definitions
from tools.git_tools import get_git_status, list_branches
from tools.relationship_tools import (
    create_relationship,
    delete_relationship,
    get_relationship_types,
    list_relationships,
)


async def main():
    # Set up logging
    setup_logging()
    logger = logging.getLogger("aichemist_mcp")

    try:
        # Create the server
        server = Server("AIchemist MCP Hub")

        # Register tools
        server.register_tool(get_git_status)
        server.register_tool(list_branches)
        server.register_tool(search_codebase)
        server.register_tool(analyze_codebase_architecture)
        server.register_tool(map_component_structure)
        server.register_tool(generate_architecture_diagram)
        server.register_tool(generate_class_diagram)
        server.register_tool(create_relationship)
        server.register_tool(list_relationships)
        server.register_tool(delete_relationship)
        server.register_tool(get_relationship_types)

        # Register resources
        server.register_resource(get_memory_bank_context)

        # Register prompts
        server.register_prompt(code_review_prompt)

        # Determine transport method from arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--http":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            logger.info(
                f"Starting AIchemist MCP Hub with HTTP transport on port {port}"
            )
            await handle_http(server, port=port)
        else:
            logger.info("Starting AIchemist MCP Hub with stdio transport")
            await handle_stdio(server)

    except Exception as e:
        logger.error(f"Error starting MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
