#!/usr/bin/env python3
"""
Calculator Agent Creator.

This script creates and configures a calculator agent using Azure AI Projects.
The agent is designed to calculate mathematical expressions using function tools.
"""

import os
import yaml
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    FunctionTool,
)
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError

from utils.user_functions import user_functions


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


def get_file_paths() -> str:
    """Get the paths for agent configuration file."""
    root_path = Path(__file__).parent
    agent_config_path = root_path / "agent.yaml"
    
    return str(agent_config_path)


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


def create_agent(agents_client, agent_config: Dict[str, Any]) -> str:
    """Create the calculator agent and return agent ID."""
    try:
        # Initialize function tool with user functions
        functions = FunctionTool(functions=user_functions)
        
        # Create agent
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name=agent_config["name"],
            instructions=agent_config["instructions"],
            description=agent_config["description"],
            temperature=agent_config["temperature"],
            tools=functions.definitions,
        )
        
        logging.info(f"Agent created successfully, ID: {agent.id}")
        return agent.id
    except AzureError as e:
        logging.error(f"Azure error during agent creation: {e}")
        raise


def main() -> None:
    """Main function to create the calculator agent."""
    logger = logging.getLogger(__name__)
    
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting calculator agent creation process...")
        
        # Validate environment
        validate_environment()
        logger.info("Environment validation passed")
        
        # Get file paths
        agent_config_path = get_file_paths()
        logger.info(f"Agent config path: {agent_config_path}")
        
        # Create Azure client
        project_client = create_azure_client()
        agents_client = project_client.agents
        
        # Load agent configuration
        agent_config = load_agent_config(agent_config_path)
        
        # Create agent
        agent_id = create_agent(agents_client, agent_config)
        
        # Success output
        logger.info("Calculator agent creation completed successfully")
        print(f"✅ Calculator agent created successfully!")
        print(f"📋 Agent ID: {agent_id}")
        print(f"📁 Agent Name: {agent_config['name']}")
        
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