import os
import yaml
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.ai.projects.models import ConnectionType
from dotenv import load_dotenv
load_dotenv()

config_path =  Path(__file__).parent / "agent.yaml"

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

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
    query_type=AzureAISearchQueryType.VECTOR_SIMPLE_HYBRID,
    top_k=10,
    filter="",
)

# Define the model deployment name
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

# Create an agent with the Azure AI Search tool
agent = project_client.agents.create_agent(
    model=model_deployment_name,
    name=config['name'],
    instructions=config["instructions"],
    description=config["description"],
    temperature=config["temperature"],
    tools=ai_search.definitions,
    tool_resources=ai_search.resources,
)
print(f"Created agent, ID: {agent.id}")

