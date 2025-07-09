#!/usr/bin/env python3
"""
Financial Data Provider Agent Creator.

This script creates and configures a financial data agent using Azure AI Projects.
The agent is designed to search and retrieve financial information from uploaded data files.
"""

import os
import yaml
import logging
import sys
from pathlib import Path
from typing import Dict, Any
import uuid

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    FilePurpose,
    FileSearchTool,
)
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('agent_creation.log')
        ]
    )
    
    # Suppress verbose HTTP request logs from Azure SDK
    logging.getLogger('azure.identity').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline.transport').setLevel(logging.WARNING)
    logging.getLogger('azure.core.rest').setLevel(logging.WARNING)
    logging.getLogger('azure.ai.projects').setLevel(logging.WARNING)


def get_file_paths() -> tuple[str, str]:
    """Get the paths for agent configuration and financial data files."""
    root_path = Path(__file__).parent
    agent_config_path = root_path / "agent.yaml"
    financial_data_path = root_path / "content_understanding/analyzer_output/financial_data.json"
    
    return str(agent_config_path), str(financial_data_path)


def validate_environment() -> None:
    """Validate that required environment variables are set."""
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


def create_azure_client() -> AIProjectClient:
    """Create and return Azure AI Project client."""
    try:
        client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        logging.info("Azure AI Project client created successfully")
        return client
    except Exception as e:
        logging.error(f"Failed to create Azure client: {e}")
        raise


def load_agent_config(config_path: str) -> Dict[str, Any]:
    """Load agent configuration from YAML file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        required_fields = ["name", "description", "instructions", "temperature"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in agent config: {missing_fields}")
        
        logging.info(f"Loaded agent configuration: {config['name']}")
        return config
    except FileNotFoundError:
        logging.error(f"Agent configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML configuration: {e}")
        raise


def upload_file(agents_client, file_path: str) -> str:
    """Upload file to Azure and return file ID."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Financial data file not found: {file_path}")
        
        file = agents_client.files.upload_and_poll(
            file_path=file_path, 
            purpose=FilePurpose.AGENTS
        )
        
        logging.info(f"File uploaded successfully, ID: {file.id}")
        return file.id
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except AzureError as e:
        logging.error(f"Azure error during file upload: {e}")
        raise


def create_vector_store(agents_client, file_id: str) -> str:
    """Create vector store and return vector store ID."""
    try:
        vector_store = agents_client.vector_stores.create_and_poll(
            file_ids=[file_id], 
            name="financial_data"
        )
        
        logging.info(f"Vector store created successfully, ID: {vector_store.id}")
        return vector_store.id
    except AzureError as e:
        logging.error(f"Azure error during vector store creation: {e}")
        raise


def create_agent(agents_client, vector_store_id: str, agent_config: Dict[str, Any]) -> str:
    """Create the financial data agent and return agent ID."""
    try:
        # Create file search tool
        file_search = FileSearchTool(vector_store_ids=[vector_store_id])
        
        # Create agent
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name=f"{agent_config['name']}-{uuid.uuid4()}",
            instructions=agent_config["instructions"],
            description=agent_config["description"],
            temperature=agent_config["temperature"],
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        
        logging.info(f"Agent created successfully, ID: {agent.id}")
        return agent.id
    except AzureError as e:
        logging.error(f"Azure error during agent creation: {e}")
        raise


def main() -> None:
    """Main function to create the financial data agent."""
    logger = logging.getLogger(__name__)
    
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting financial agent creation process...")
        
        # Validate environment
        validate_environment()
        logger.info("Environment validation passed")
        
        # Get file paths
        agent_config_path, financial_data_path = get_file_paths()
        logger.info(f"Agent config path: {agent_config_path}")
        logger.info(f"Financial data path: {financial_data_path}")
        
        # Create Azure client
        project_client = create_azure_client()
        agents_client = project_client.agents
        
        # Load agent configuration
        agent_config = load_agent_config(agent_config_path)
        
        # Upload file
        file_id = upload_file(agents_client, financial_data_path)
        
        # Create vector store
        vector_store_id = create_vector_store(agents_client, file_id)
        
        # Create agent
        agent_id = create_agent(agents_client, vector_store_id, agent_config)
        
        # Success output
        logger.info("Financial agent creation completed successfully")
        print(f"✅ Financial agent created successfully!")
        print(f"📋 Agent ID: {agent_id}")
        print(f"📁 Agent Name: {agent_config['name']}")
        print(f"🔍 Vector Store: financial_data")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"❌ File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during agent creation: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()