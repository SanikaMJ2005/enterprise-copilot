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
            cleaned[k] = [
                clean_schema(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            cleaned[k] = v
    return cleaned


async def run_copilot():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["src/mcp_server/server.py"],
        env=os.environ.copy(),
    )

    print("🔌 Connecting to local MCP Server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to MCP Server!")

            # Fetch available tools
            mcp_tools = await session.list_tools()
            print(f"🛠️  Loaded {len(mcp_tools.tools)} MCP Tools:")
            for tool in mcp_tools.tools:
                print(f"   - {tool.name}")

            # Format tools for Gemini API
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

            config = types.GenerateContentConfig(
                tools=gemini_tools,
                temperature=0.2,
            )

            # Conversation history buffer
            chat_history = []

            print("\n" + "=" * 60)
            print("🚀 Enterprise Copilot CLI Ready! (Type 'exit' or 'quit' to stop)")
            print("=" * 60 + "\n")

            while True:
                try:
                    user_input = input("👤 You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting...")
                    break

                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit"):
                    print("👋 Goodbye!")
                    break

                # Add user query to conversation history
                chat_history.append(
                    types.Content(
                        role="user", parts=[types.Part.from_text(text=user_input)]
                    )
                )

                # Tool-execution loop for the current turn
                while True:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=chat_history,
                        config=config,
                    )

                    if response.function_calls:
                        # Append assistant's function call decision to history
                        chat_history.append(response.candidates[0].content)
                        function_responses = []

                        for call in response.function_calls:
                            print(f"\n🤖 [Calling Tool]: {call.name}")
                            print(f"   Args: {call.args}")

                            # Execute tool call via MCP
                            result = await session.call_tool(call.name, call.args)
                            result_text = (
                                result.content[0].text if result.content else ""
                            )
                            print(f"⚡ [Result]:\n{result_text}\n")

                            function_responses.append(
                                types.Part.from_function_response(
                                    name=call.name,
                                    response={"result": result_text},
                                )
                            )

                        # Provide function results back to Gemini
                        chat_history.append(
                            types.Content(role="user", parts=function_responses)
                        )
                    else:
                        print(f"\n🤖 Copilot:\n{response.text}\n")
                        # Store final assistant text response in context history
                        chat_history.append(
                            types.Content(
                                role="model",
                                parts=[types.Part.from_text(text=response.text)],
                            )
                        )
                        break


if __name__ == "__main__":
    asyncio.run(run_copilot())