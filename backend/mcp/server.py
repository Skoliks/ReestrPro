from __future__ import annotations

from typing import Any

from backend.mcp.tools import ask_registry, get_document_card, search_registry


def create_mcp_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP SDK is not installed. Install project requirements first: "
            "pip install -r requirements.txt"
        ) from exc

    server = FastMCP("ReestrPro")

    server.tool()(search_registry)
    server.tool()(get_document_card)
    server.tool()(ask_registry)

    return server


def main() -> None:
    server = create_mcp_server()
    server.run()


if __name__ == "__main__":
    main()
