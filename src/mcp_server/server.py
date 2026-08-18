import os
import chromadb
from chromadb.utils import embedding_functions
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server (v2.0+)
mcp = FastMCP("Enterprise-Workflow-Server")


# Tool 1: RAG Document Search
@mcp.tool()
def search_company_policies(query: str) -> str:
    """Search internal company policies, IT standards, and SLAs using RAG vector search.

    Args:
        query: Natural language search query about company policies or guidelines.
    """
    db_path = os.path.join("data", "chroma_db")
    if not os.path.exists(db_path):
        return "Error: Policy database not indexed yet."

    chroma_client = chromadb.PersistentClient(path=db_path)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    try:
        collection = chroma_client.get_collection(
            name="company_policies", embedding_function=embedding_fn
        )
        results = collection.query(query_texts=[query], n_results=2)
        documents = results.get("documents", [[]])[0]
        if not documents:
            return "No relevant policies found."
        return "\n\n---\n\n".join(documents)
    except Exception as e:
        return f"Error querying policy database: {str(e)}"


# Tool 2: Check System Operational Status
@mcp.tool()
def get_system_status(service_name: str) -> str:
    """Check the operational status of a company service or database.

    Args:
        service_name: Name of the service (e.g. 'auth-db', 'payment-gateway', 'api-router')
    """
    status_db = {
        "auth-db": "Operational | Latency: 12ms",
        "payment-gateway": "Degraded | Error Rate: 4.5%",
        "api-router": "Operational | Latency: 5ms",
    }
    key = service_name.lower().strip()
    return status_db.get(
        key, f"Service '{service_name}' not found in monitoring registry."
    )


# Tool 3: Create an Incident Ticket
@mcp.tool()
def create_incident_ticket(title: str, severity: str, description: str) -> str:
    """Create a new incident ticket for system outages or bugs.

    Args:
        title: Brief summary of the issue
        severity: Priority level ('P1', 'P2', 'P3')
        description: Detailed explanation of what failed
    """
    ticket_id = f"INC-{os.urandom(2).hex().upper()}"
    return (
        f"Success! Incident Ticket Created:\n"
        f"- Ticket ID: {ticket_id}\n"
        f"- Title: {title}\n"
        f"- Severity: {severity}\n"
        f"- Status: Open"
    )


if __name__ == "__main__":
    mcp.run()