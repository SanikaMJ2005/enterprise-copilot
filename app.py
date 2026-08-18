import asyncio
import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Import MCP Client utilities
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import Google Gemini SDK
from google import genai
from google.genai import types

# Import direct MCP tool functions for tab execution
from src.mcp_server.server import (
    search_company_policies,
    get_system_status,
    create_incident_ticket,
)

# Robust environment variable loading
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

# Streamlit Page Setup - Modern Wide Layout
st.set_page_config(
    page_title="Enterprise Copilot • FastMCP Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background gradient overlay */
.stApp {
    background: radial-gradient(circle at 15% 15%, rgba(139, 92, 246, 0.18), transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.15), transparent 45%),
                #0F172A;
}

/* Hero Title Banner */
.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.85));
    backdrop-filter: blur(16px);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px -10px rgba(139, 92, 246, 0.3);
}

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #C4B5FD, #38BDF8, #34D399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 0.95rem;
    margin-top: 6px;
    margin-bottom: 16px;
    font-weight: 500;
}

.badge-container {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.tech-badge {
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #C4B5FD;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.tech-badge.cyan {
    background: rgba(6, 182, 212, 0.15);
    border-color: rgba(6, 182, 212, 0.4);
    color: #7DD3FC;
}

.tech-badge.emerald {
    background: rgba(16, 185, 129, 0.15);
    border-color: rgba(16, 185, 129, 0.4);
    color: #6EE7B7;
}

/* Sidebar Card Buttons Styling */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95)) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    text-align: left !important;
    white-space: pre-wrap !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #F1F5F9 !important;
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    transition: all 0.3s ease !important;
    margin-bottom: 6px !important;
    width: 100% !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    border-color: rgba(167, 139, 250, 0.7) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3) !important;
    background: linear-gradient(135deg, rgba(40, 53, 76, 0.9), rgba(20, 30, 55, 0.98)) !important;
}

/* Tab Panels & Cards */
.tab-panel-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-top: 10px;
    backdrop-filter: blur(12px);
}

.result-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(6, 182, 212, 0.4);
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
    color: #E2E8F0;
    line-height: 1.6;
}

.service-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}

/* Chat Messages */
div[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 14px;
    backdrop-filter: blur(8px);
}

/* Tool execution status expanders */
div[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(6, 182, 212, 0.35) !important;
    border-radius: 12px !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0F172A;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #8B5CF6;
}
</style>
""", unsafe_allow_html=True)

# Render Hero Header Banner
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🤖 Enterprise Copilot Dashboard</h1>
    <p class="hero-subtitle">Intelligent agentic assistant powered by Model Context Protocol (MCP) & Google Gemini AI</p>
    <div class="badge-container">
        <span class="tech-badge">✨ Gemini 2.5 Flash</span>
        <span class="tech-badge cyan">⚡ FastMCP Workflow Engine</span>
        <span class="tech-badge emerald">🔍 ChromaDB Vector Search</span>
    </div>
</div>
""", unsafe_allow_html=True)


def clean_schema(schema):
    """Clean JSON Schema for Gemini SDK compatibility."""
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


async def mcp_agent_loop(user_input):
    """Launches MCP server process and manages tool call interactions with Gemini."""
    # Launch MCP Server Process with module-level environment access
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["src/mcp_server/server.py"],
        env={"PYTHONPATH": os.getcwd(), **os.environ},
    )

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    final_text = None
    tool_calls_executed = []

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Load available tools from local FastMCP server
                mcp_tools = await session.list_tools()
                gemini_tools = [
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name=tool.name,
                                description=tool.description,
                                parameters=clean_schema(tool.inputSchema),
                            )
                        ]
                    )
                    for tool in mcp_tools.tools
                ]

                config = types.GenerateContentConfig(
                    tools=gemini_tools,
                    temperature=0.2,
                )

                # Reconstruct full conversation context for Gemini
                gemini_contents = []
                for msg in st.session_state.messages:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_contents.append(
                        types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                    )

                # Tool execution loop
                while True:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=gemini_contents,
                        config=config,
                    )

                    if response.function_calls:
                        gemini_contents.append(response.candidates[0].content)
                        function_responses = []

                        for call in response.function_calls:
                            # Render live status container for UI feedback
                            with st.status(f"⚡ Executing Tool: `{call.name}`", expanded=True) as status:
                                st.write("**Arguments:**", call.args)
                                # Execute tool call over MCP session
                                result = await session.call_tool(call.name, call.args)

                                result_text = ""
                                if result and result.content:
                                    texts = [item.text for item in result.content if hasattr(item, "text")]
                                    result_text = "\n".join(texts) if texts else str(result.content)

                                st.write("**Result:**", result_text)
                                status.update(label=f"✅ Tool Completed: `{call.name}`", state="complete", expanded=False)

                            tool_calls_executed.append({"name": call.name, "args": call.args, "result": result_text})

                            function_responses.append(
                                types.Part.from_function_response(
                                    name=call.name,
                                    response={"result": result_text},
                                )
                            )

                        gemini_contents.append(
                            types.Content(role="user", parts=function_responses)
                        )
                    else:
                        final_text = response.text
                        break

    except (BaseExceptionGroup, ExceptionGroup):
        # Ignore subprocess teardown exception if final response was retrieved
        pass
    except Exception as e:
        st.error(f"MCP Connection Error: {str(e)}")

    if final_text is not None:
        return final_text, tool_calls_executed

    return "Failed to complete request.", []


def handle_user_query(prompt: str):
    """Executes the async MCP workflow in standard event loop."""
    return asyncio.run(mcp_agent_loop(prompt))


# Session State Initialization for Active Navigation View
if "current_view" not in st.session_state:
    st.session_state.current_view = "💬 AI Copilot Chat"

if "messages" not in st.session_state:
    st.session_state.messages = []


# Sidebar Control Center with Interactive Clickable Tool Cards
with st.sidebar:
    st.markdown("### ⚡ Control Center")
    st.markdown("<p style='color: #94A3B8; font-size: 0.85rem;'>Active Model Context Protocol Tools</p>", unsafe_allow_html=True)
    
    # Interactive Sidebar Buttons styled as Cards
    if st.button("💬 AI Copilot Chat\n\nAutomated FastMCP agent workflow powered by Gemini 2.5 Flash.", key="nav_chat"):
        st.session_state.current_view = "💬 AI Copilot Chat"
        st.rerun()

    if st.button("🔍 search_company_policies  🟢\n\nChromaDB RAG Vector Search across IT standards, SLAs, & security policies.", key="nav_rag"):
        st.session_state.current_view = "🔍 Policy Search (RAG)"
        st.rerun()

    if st.button("📊 get_system_status  🟢\n\nReal-time health & latency monitoring for auth-db, payment-gateway, api-router.", key="nav_status"):
        st.session_state.current_view = "📊 System Health Monitor"
        st.rerun()

    if st.button("🎫 create_incident_ticket  🟢\n\nAutomated ITSM ticket creation for critical outages and performance bugs.", key="nav_ticket"):
        st.session_state.current_view = "🎫 Create Incident Ticket"
        st.rerun()

    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Messages", value=len(st.session_state.get("messages", [])))
    with col2:
        mcp_count = sum(len(m.get("tools", [])) for m in st.session_state.get("messages", []))
        st.metric(label="Tool Calls", value=mcp_count)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", key="nav_clear", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Top Horizontal Mode Switcher Buttons
view_options = [
    "💬 AI Copilot Chat",
    "🔍 Policy Search (RAG)",
    "📊 System Health Monitor",
    "🎫 Create Incident Ticket"
]

cols = st.columns(4)
for i, option in enumerate(view_options):
    with cols[i]:
        btn_style = "primary" if st.session_state.current_view == option else "secondary"
        if st.button(option, key=f"top_nav_{i}", use_container_width=True):
            st.session_state.current_view = option
            st.rerun()

st.divider()

# ----------------------------------------------------
# VIEW 1: AI Copilot Chat Interface
# ----------------------------------------------------
if st.session_state.current_view == "💬 AI Copilot Chat":
    st.markdown("### 💬 AI Copilot Agent Chat")
    st.caption("Ask queries in natural language. Gemini automatically determines when to call MCP tools.")

    # Display Conversation History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "tools" in message and message["tools"]:
                for t in message["tools"]:
                    with st.expander(f"⚡ Tool executed: `{t['name']}`"):
                        st.write("**Arguments:**", t["args"])
                        st.write("**Output:**", t["result"])
            st.markdown(message["content"])

    # Chat Input Interface
    if prompt := st.chat_input("Ask about policies, check service status, or create incident tickets..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Executing FastMCP agent workflow..."):
                st.session_state.messages.append({"role": "user", "content": prompt, "tools": []})
                reply, tools_used = handle_user_query(prompt)
                if reply:
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply, "tools": tools_used})
                st.rerun()

# ----------------------------------------------------
# VIEW 2: Direct Policy Search (RAG)
# ----------------------------------------------------
elif st.session_state.current_view == "🔍 Policy Search (RAG)":
    st.markdown("### 🔍 RAG Vector Search — Company Policy Knowledgebase")
    st.caption("Directly query ChromaDB vector index for IT standards, SLAs, and security compliance.")
    
    rag_query = st.text_input("Enter search query:", placeholder="e.g. What is the SLA for a P1 critical incident?")
    
    col_search, col_preset1, col_preset2 = st.columns([1.2, 1, 1])
    with col_search:
        do_search = st.button("🔎 Search Policy Vector Store", key="btn_run_rag", use_container_width=True)
    with col_preset1:
        if st.button("📋 Sample: Incident SLAs", key="preset_sla", use_container_width=True):
            rag_query = "What is the SLA for P1, P2, and P3 incidents?"
            do_search = True
    with col_preset2:
        if st.button("🔒 Sample: Security Policy", key="preset_sec", use_container_width=True):
            rag_query = "Password complexity and security policy requirements"
            do_search = True

    if do_search and rag_query:
        with st.spinner("Searching ChromaDB collection..."):
            result = search_company_policies(rag_query)
            st.markdown("#### 📄 Search Results")
            st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# VIEW 3: Real-Time System Health Monitor
# ----------------------------------------------------
elif st.session_state.current_view == "📊 System Health Monitor":
    st.markdown("### 📊 Real-Time Operational Service Health")
    st.caption("Check infrastructure component status, latency metrics, and error rates.")
    
    col_svc1, col_svc2, col_svc3 = st.columns(3)
    
    with col_svc1:
        st.markdown("""
        <div class="service-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#F1F5F9;">🔐 auth-db</h4>
                <span style="height:10px; width:10px; background-color:#10B981; border-radius:50%; display:inline-block; box-shadow:0 0 10px #10B981;"></span>
            </div>
            <p style="color:#94A3B8; font-size:0.82rem; margin-top:6px;">Authentication & User Data Store</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check auth-db", key="btn_auth_mon", use_container_width=True):
            res = get_system_status("auth-db")
            st.success(f"**Status:** {res}")
            
    with col_svc2:
        st.markdown("""
        <div class="service-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#F1F5F9;">💳 payment-gateway</h4>
                <span style="height:10px; width:10px; background-color:#F59E0B; border-radius:50%; display:inline-block; box-shadow:0 0 10px #F59E0B;"></span>
            </div>
            <p style="color:#94A3B8; font-size:0.82rem; margin-top:6px;">Payment Processing & Checkout API</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check payment-gateway", key="btn_pay_mon", use_container_width=True):
            res = get_system_status("payment-gateway")
            st.warning(f"**Status:** {res}")

    with col_svc3:
        st.markdown("""
        <div class="service-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#F1F5F9;">🌐 api-router</h4>
                <span style="height:10px; width:10px; background-color:#10B981; border-radius:50%; display:inline-block; box-shadow:0 0 10px #10B981;"></span>
            </div>
            <p style="color:#94A3B8; font-size:0.82rem; margin-top:6px;">Core Gateway & Load Balancer</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check api-router", key="btn_api_mon", use_container_width=True):
            res = get_system_status("api-router")
            st.success(f"**Status:** {res}")

    st.divider()
    st.markdown("#### 🔍 Custom Service Lookup")
    custom_service = st.text_input("Service Name:", value="payment-gateway", key="input_svc_lookup")
    if st.button("Query Service Monitor", key="btn_custom_svc"):
        res = get_system_status(custom_service)
        st.info(f"**Status Report:** {res}")

# ----------------------------------------------------
# VIEW 4: Automated Incident Ticket Creation Form
# ----------------------------------------------------
elif st.session_state.current_view == "🎫 Create Incident Ticket":
    st.markdown("### 🎫 Create Incident Ticket")
    st.caption("File an ITSM incident ticket directly into the automated workflow engine.")
    
    with st.form("incident_ticket_form"):
        ticket_title = st.text_input("Issue Title:", placeholder="e.g. Payment gateway latency spikes on checkout")
        ticket_severity = st.selectbox("Severity Level:", ["P1 (Critical Outage)", "P2 (High Impact)", "P3 (Low Minor)"])
        ticket_desc = st.text_area("Detailed Description:", placeholder="Describe the failure, impact, and affected systems...")
        
        submitted = st.form_submit_button("🚀 Submit Incident Ticket", use_container_width=True)
        
        if submitted:
            if not ticket_title or not ticket_desc:
                st.error("Please fill in both title and description.")
            else:
                sev_code = ticket_severity.split()[0]
                res = create_incident_ticket(ticket_title, sev_code, ticket_desc)
                st.balloons()
                st.markdown(f'<div class="result-card" style="border-color: #10B981;">{res}</div>', unsafe_allow_html=True)