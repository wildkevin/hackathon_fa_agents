import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.ai.projects.models import ConnectionType
from azure.ai.agents.models import MessageRole, ListSortOrder
from dotenv import load_dotenv

load_dotenv()

# Retrieve the endpoint from environment variables
project_endpoint = os.environ["PROJECT_ENDPOINT"]

# Initialize the AIProjectClient
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
)

# Define the Azure AI Search connection ID and index name
azure_ai_conn_id = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH).id

# find the index name in your AI Search Azure resource page under Search Management -> Indexes
index_name = "tesco_report_agent"

# Initialize the Azure AI Search tool
ai_search = AzureAISearchTool(
    index_connection_id=azure_ai_conn_id,
    index_name=index_name,
    query_type=AzureAISearchQueryType.VECTOR_SIMPLE_HYBRID,  # Use SIMPLE query type
    top_k=10,  # Retrieve the top 3 results
    filter="",  # Optional filter for search results
)

# Define the model deployment name
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

# Create an agent with the Azure AI Search tool
agent = project_client.agents.create_agent(
    model=model_deployment_name,
    name="rag-agent",
    instructions="""use the azure_index_browser tool to retrieve relevant documents,then base the retrieve document reply user's query,If the information required to answer the question is not found in the search results, respond with:
"I'm sorry, I couldn't find enough information to answer your question.""",
    tools=ai_search.definitions,
    tool_resources=ai_search.resources,
)
print(f"Created agent, ID: {agent.id}")

# Create a thread for communication
thread = project_client.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

