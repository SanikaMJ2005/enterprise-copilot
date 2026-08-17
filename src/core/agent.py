import asyncio
import os
import sys
from dotenv import load_dotenv

# Import MCP Client utilities
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import Google Gemini SDK
from google import genai
from google.genai import types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def clean_schema(schema):
    """Clean JSON Schema for Google Gemini API by removing unsupported fields like additionalProperties."""
    if not isinstance(schema, dict):
        return schema
    cleaned = {}
    for k, v in schema.items():
        if k in ("additionalProperties", "additional_properties", "$schema"):
            continue
        if isinstance(v, dict):
            cleaned[k] = clean_schema(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_schema(item) if isinstance(item, dict) else item for item in v]
        else:
            cleaned[k] = v
    return cleaned


async def run_copilot():
    # 1. Define how to launch our local MCP server as a subprocess
    server_params = StdioServerParameters(
        command=sys.executable,  # Uses current active Python inside venv
        args=["src/mcp_server/server.py"],
        env=os.environ.copy(),
    )

    print("🔌 Connecting to local MCP Server...")

    # 2. Establish connection to MCP Server over stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected! Fetching available tools from MCP Server...")

            # 3. List tools registered on the server
            mcp_tools = await session.list_tools()
            print(f"🛠️  Found {len(mcp_tools.tools)} MCP Tools:")
            for tool in mcp_tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            # 4. Prompt the user for input
            user_prompt = "Check the status of payment-gateway. If it is degraded, open a P1 ticket describing the issue."
            print(f"\n💬 User Query: '{user_prompt}'\n")

            # 5. Convert MCP tools to Gemini function declarations
            gemini_tools = []
            for tool in mcp_tools.tools:
                gemini_tools.append(
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name=tool.name,
                                description=tool.description,
                                parameters=clean_schema(tool.inputSchema),
                            )
                        ]
                    )
                )

            # 6. Send request to Gemini LLM with tools enabled (with multi-turn tool calling)
            contents = [user_prompt]
            config = types.GenerateContentConfig(
                tools=gemini_tools,
                temperature=0.2,
            )

            while True:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=config,
                )

                if response.function_calls:
                    contents.append(response.candidates[0].content)
                    function_responses = []

                    for call in response.function_calls:
                        print(f"🤖 AI Decided to call tool: {call.name}")
                        print(f"   Arguments: {call.args}")

                        # Execute the tool call via MCP Session
                        result = await session.call_tool(call.name, call.args)
                        result_text = result.content[0].text if result.content else ""
                        print(f"⚡ MCP Execution Result:\n{result_text}\n")

                        function_responses.append(
                            types.Part.from_function_response(
                                name=call.name,
                                response={"result": result_text},
                            )
                        )

                    contents.append(types.Content(role="user", parts=function_responses))
                else:
                    print(f"🤖 Final AI Response:\n{response.text}")
                    break


if __name__ == "__main__":
    asyncio.run(run_copilot())