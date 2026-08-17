import asyncio
import os
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

# 1. Initialize core MCP Server instance
server = Server("Enterprise-Workflow-Server")


# 2. Register available tools
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Expose available tools and their JSON schemas to the LLM."""
    return [
        types.Tool(
            name="get_system_status",
            description="Check operational status of a company service or database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service (e.g. 'auth-db', 'payment-gateway')",
                    }
                },
                "required": ["service_name"],
            },
        ),
        types.Tool(
            name="create_incident_ticket",
            description="Create a new incident ticket for outages or bugs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Brief summary of the issue"},
                    "severity": {"type": "string", "description": "Priority level ('P1', 'P2', 'P3')"},
                    "description": {"type": "string", "description": "Detailed error log or issue summary"},
                },
                "required": ["title", "severity", "description"],
            },
        ),
    ]


# 3. Handle tool execution requests from the LLM
@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute the requested tool and return output text."""
    if not arguments:
        arguments = {}

    if name == "get_system_status":
        service_name = arguments.get("service_name", "").lower().strip()
        status_db = {
            "auth-db": "Operational | Latency: 12ms",
            "payment-gateway": "Degraded | Error Rate: 4.5%",
            "api-router": "Operational | Latency: 5ms",
        }
        result = status_db.get(
            service_name, f"Service '{service_name}' not found in registry."
        )
        return [types.TextContent(type="text", text=result)]

    elif name == "create_incident_ticket":
        title = arguments.get("title", "No Title")
        severity = arguments.get("severity", "P3")
        ticket_id = f"INC-{os.urandom(2).hex().upper()}"
        result = f"Success! Created Ticket:\n- Ticket ID: {ticket_id}\n- Title: {title}\n- Severity: {severity}"
        return [types.TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


# 4. Run the server over standard input/output (stdio)
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Enterprise-Workflow-Server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())