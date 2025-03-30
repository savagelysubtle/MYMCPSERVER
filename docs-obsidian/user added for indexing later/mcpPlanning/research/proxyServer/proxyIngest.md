Directory structure:
└── sparfenyuk-mcp-proxy/
    └── src/
        └── mcp_proxy/
            ├── __init__.py
            ├── __main__.py
            ├── proxy_server.py
            ├── py.typed
            ├── sse_client.py
            └── sse_server.py

================================================
File: src/mcp_proxy/__init__.py
================================================
"""Library for proxying MCP servers across different transports."""



================================================
File: src/mcp_proxy/__main__.py
================================================
"""The entry point for the mcp-proxy application. It sets up the logging and runs the main function.

Two ways to run the application:
1. Run the application as a module `uv run -m mcp_proxy`
2. Run the application as a package `uv run mcp-proxy`

"""

import argparse
import asyncio
import logging
import os
import sys
import typing as t

from mcp.client.stdio import StdioServerParameters

from .sse_client import run_sse_client
from .sse_server import SseServerSettings, run_sse_server

logging.basicConfig(level=logging.DEBUG)
SSE_URL: t.Final[str | None] = os.getenv(
    "SSE_URL",
    None,
)


def main() -> None:
    """Start the client using asyncio."""
    parser = argparse.ArgumentParser(
        description=(
            "Start the MCP proxy in one of two possible modes: as an SSE or stdio client."
        ),
        epilog=(
            "Examples:\n"
            "  mcp-proxy http://localhost:8080/sse\n"
            "  mcp-proxy --headers Authorization 'Bearer YOUR_TOKEN' http://localhost:8080/sse\n"
            "  mcp-proxy --sse-port 8080 -- your-command --arg1 value1 --arg2 value2\n"
            "  mcp-proxy your-command --sse-port 8080 -e KEY VALUE -e ANOTHER_KEY ANOTHER_VALUE\n"
            "  mcp-proxy your-command --sse-port 8080 --allow-origin='*'\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "command_or_url",
        help=(
            "Command or URL to connect to. When a URL, will run an SSE client, "
            "otherwise will run the given command and connect as a stdio client. "
            "See corresponding options for more details."
        ),
        nargs="?",  # Required below to allow for coming form env var
        default=SSE_URL,
    )

    sse_client_group = parser.add_argument_group("SSE client options")
    sse_client_group.add_argument(
        "-H",
        "--headers",
        nargs=2,
        action="append",
        metavar=("KEY", "VALUE"),
        help="Headers to pass to the SSE server. Can be used multiple times.",
        default=[],
    )

    stdio_client_options = parser.add_argument_group("stdio client options")
    stdio_client_options.add_argument(
        "args",
        nargs="*",
        help="Any extra arguments to the command to spawn the server",
    )
    stdio_client_options.add_argument(
        "-e",
        "--env",
        nargs=2,
        action="append",
        metavar=("KEY", "VALUE"),
        help="Environment variables used when spawning the server. Can be used multiple times.",
        default=[],
    )
    stdio_client_options.add_argument(
        "--pass-environment",
        action=argparse.BooleanOptionalAction,
        help="Pass through all environment variables when spawning the server.",
        default=False,
    )

    sse_server_group = parser.add_argument_group("SSE server options")
    sse_server_group.add_argument(
        "--sse-port",
        type=int,
        default=0,
        help="Port to expose an SSE server on. Default is a random port",
    )
    sse_server_group.add_argument(
        "--sse-host",
        default="127.0.0.1",
        help="Host to expose an SSE server on. Default is 127.0.0.1",
    )
    sse_server_group.add_argument(
        "--allow-origin",
        nargs="+",
        default=[],
        help="Allowed origins for the SSE server. Can be used multiple times. Default is no CORS allowed.",  # noqa: E501
    )

    args = parser.parse_args()

    if not args.command_or_url:
        parser.print_help()
        sys.exit(1)

    if (
        SSE_URL
        or args.command_or_url.startswith("http://")
        or args.command_or_url.startswith("https://")
    ):
        # Start a client connected to the SSE server, and expose as a stdio server
        logging.debug("Starting SSE client and stdio server")
        headers = dict(args.headers)
        if api_access_token := os.getenv("API_ACCESS_TOKEN", None):
            headers["Authorization"] = f"Bearer {api_access_token}"
        asyncio.run(run_sse_client(args.command_or_url, headers=headers))
        return

    # Start a client connected to the given command, and expose as an SSE server
    logging.debug("Starting stdio client and SSE server")

    # The environment variables passed to the server process
    env: dict[str, str] = {}
    # Pass through current environment variables if configured
    if args.pass_environment:
        env.update(os.environ)
    # Pass in and override any environment variables with those passed on the command line
    env.update(dict(args.env))

    stdio_params = StdioServerParameters(
        command=args.command_or_url,
        args=args.args,
        env=env,
    )
    sse_settings = SseServerSettings(
        bind_host=args.sse_host,
        port=args.sse_port,
        allow_origins=args.allow_origin if len(args.allow_origin) > 0 else None,
    )
    asyncio.run(run_sse_server(stdio_params, sse_settings))


if __name__ == "__main__":
    main()



================================================
File: src/mcp_proxy/proxy_server.py
================================================
"""Create an MCP server that proxies requests throgh an MCP client.

This server is created independent of any transport mechanism.
"""

import typing as t

from mcp import server, types
from mcp.client.session import ClientSession


async def create_proxy_server(remote_app: ClientSession) -> server.Server[object]:  # noqa: C901
    """Create a server instance from a remote app."""
    response = await remote_app.initialize()
    capabilities = response.capabilities

    app: server.Server[object] = server.Server(name=response.serverInfo.name)

    if capabilities.prompts:

        async def _list_prompts(_: t.Any) -> types.ServerResult:  # noqa: ANN401
            result = await remote_app.list_prompts()
            return types.ServerResult(result)

        app.request_handlers[types.ListPromptsRequest] = _list_prompts

        async def _get_prompt(req: types.GetPromptRequest) -> types.ServerResult:
            result = await remote_app.get_prompt(req.params.name, req.params.arguments)
            return types.ServerResult(result)

        app.request_handlers[types.GetPromptRequest] = _get_prompt

    if capabilities.resources:

        async def _list_resources(_: t.Any) -> types.ServerResult:  # noqa: ANN401
            result = await remote_app.list_resources()
            return types.ServerResult(result)

        app.request_handlers[types.ListResourcesRequest] = _list_resources

        # list_resource_templates() is not implemented in the client
        # async def _list_resource_templates(_: t.Any) -> types.ServerResult:
        #     result = await remote_app.list_resource_templates()
        #     return types.ServerResult(result)

        # app.request_handlers[types.ListResourceTemplatesRequest] = _list_resource_templates

        async def _read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
            result = await remote_app.read_resource(req.params.uri)
            return types.ServerResult(result)

        app.request_handlers[types.ReadResourceRequest] = _read_resource

    if capabilities.logging:

        async def _set_logging_level(req: types.SetLevelRequest) -> types.ServerResult:
            await remote_app.set_logging_level(req.params.level)
            return types.ServerResult(types.EmptyResult())

        app.request_handlers[types.SetLevelRequest] = _set_logging_level

    if capabilities.resources:

        async def _subscribe_resource(req: types.SubscribeRequest) -> types.ServerResult:
            await remote_app.subscribe_resource(req.params.uri)
            return types.ServerResult(types.EmptyResult())

        app.request_handlers[types.SubscribeRequest] = _subscribe_resource

        async def _unsubscribe_resource(req: types.UnsubscribeRequest) -> types.ServerResult:
            await remote_app.unsubscribe_resource(req.params.uri)
            return types.ServerResult(types.EmptyResult())

        app.request_handlers[types.UnsubscribeRequest] = _unsubscribe_resource

    if capabilities.tools:

        async def _list_tools(_: t.Any) -> types.ServerResult:  # noqa: ANN401
            tools = await remote_app.list_tools()
            return types.ServerResult(tools)

        app.request_handlers[types.ListToolsRequest] = _list_tools

        async def _call_tool(req: types.CallToolRequest) -> types.ServerResult:
            try:
                result = await remote_app.call_tool(
                    req.params.name,
                    (req.params.arguments or {}),
                )
                return types.ServerResult(result)
            except Exception as e:  # noqa: BLE001
                return types.ServerResult(
                    types.CallToolResult(
                        content=[types.TextContent(type="text", text=str(e))],
                        isError=True,
                    ),
                )

        app.request_handlers[types.CallToolRequest] = _call_tool

    async def _send_progress_notification(req: types.ProgressNotification) -> None:
        await remote_app.send_progress_notification(
            req.params.progressToken,
            req.params.progress,
            req.params.total,
        )

    app.notification_handlers[types.ProgressNotification] = _send_progress_notification

    async def _complete(req: types.CompleteRequest) -> types.ServerResult:
        result = await remote_app.complete(
            req.params.ref,
            req.params.argument.model_dump(),
        )
        return types.ServerResult(result)

    app.request_handlers[types.CompleteRequest] = _complete

    return app



================================================
File: src/mcp_proxy/py.typed
================================================



================================================
File: src/mcp_proxy/sse_client.py
================================================
"""Create a local server that proxies requests to a remote server over SSE."""

from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.server.stdio import stdio_server

from .proxy_server import create_proxy_server


async def run_sse_client(url: str, headers: dict[str, Any] | None = None) -> None:
    """Run the SSE client.

    Args:
        url: The URL to connect to.
        headers: Headers for connecting to MCP server.

    """
    async with sse_client(url=url, headers=headers) as streams, ClientSession(*streams) as session:
        app = await create_proxy_server(session)
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )



================================================
File: src/mcp_proxy/sse_server.py
================================================
"""Create a local SSE server that proxies requests to a stdio MCP server."""

from dataclasses import dataclass
from typing import Literal

import uvicorn
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Mount, Route

from .proxy_server import create_proxy_server


@dataclass
class SseServerSettings:
    """Settings for the server."""

    bind_host: str
    port: int
    allow_origins: list[str] | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


def create_starlette_app(
    mcp_server: Server[object],
    *,
    allow_origins: list[str] | None = None,
    debug: bool = False,
) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    middleware: list[Middleware] = []
    if allow_origins is not None:
        middleware.append(
            Middleware(
                CORSMiddleware,
                allow_origins=allow_origins,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        )

    return Starlette(
        debug=debug,
        middleware=middleware,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


async def run_sse_server(
    stdio_params: StdioServerParameters,
    sse_settings: SseServerSettings,
) -> None:
    """Run the stdio client and expose an SSE server.

    Args:
        stdio_params: The parameters for the stdio client that spawns a stdio server.
        sse_settings: The settings for the SSE server that accepts incoming requests.

    """
    async with stdio_client(stdio_params) as streams, ClientSession(*streams) as session:
        mcp_server = await create_proxy_server(session)

        # Bind SSE request handling to MCP server
        starlette_app = create_starlette_app(
            mcp_server,
            allow_origins=sse_settings.allow_origins,
            debug=(sse_settings.log_level == "DEBUG"),
        )

        # Configure HTTP server
        config = uvicorn.Config(
            starlette_app,
            host=sse_settings.bind_host,
            port=sse_settings.port,
            log_level=sse_settings.log_level.lower(),
        )
        http_server = uvicorn.Server(config)
        await http_server.serve()


