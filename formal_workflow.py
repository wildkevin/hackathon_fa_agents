import os
import asyncio
import datetime

from azure.ai.agents.models import FilePurpose
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import (
    AgentRegistry, AzureAIAgent, AzureAIAgentSettings,
    StandardMagenticManager, Agent,
)
from semantic_kernel.agents.orchestration.magentic import MagenticOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents import StreamingChatMessageContent, ChatMessageContent

# load .env variables
from dotenv import load_dotenv
load_dotenv()

# Flag to indicate if a new message is being received
is_new_message = True

def streaming_agent_response_callback(message: StreamingChatMessageContent, is_final: bool) -> None:
    """Observer function to print the messages from the agents.

    Args:
        message (StreamingChatMessageContent): The streaming message content from the agent.
        is_final (bool): Indicates if this is the final part of the message.
    """
    global is_new_message
    if is_new_message:
        print(f"# {message.name}")
        is_new_message = False
    print(message.content, end="", flush=True)
    if is_final:
        print()
        is_new_message = True

def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"**{message.name}**\n{message.content}")

async def get_agents(kernel: Kernel, settings: AzureAIAgentSettings, client: object) -> list[Agent]:
    """Create and return all agents for the financial analysis workflow.
    
    Args:
        kernel: The semantic kernel instance
        settings: Azure AI Agent settings
        client: Azure AI Agent client
        fin_statement_file_id: File ID of the uploaded financial statement
        
    Returns:
        list: List of initialized agents
    """

    # Sector Retrieval Agent
    agent_id = ""
    rag_agent = await client.agents.get_agent(agent_id)
    print(f"✅ Initialized RAG Agent agent")

    # Metric Retrieval Analyst
    agent_id = "asst_v6rsuv5M4G26vKwD1Cio6cOd"
    metric_retrieval_analyst = await client.agents.get_agent(agent_id)
    print(f"✅ Initialized Metric Retrieval Analyst agent")

    # Formula Provider
    agent_id = "asst_62cjkb6GOd6ryvTcFtlcM3EQ"
    formula_provider = await client.agents.get_agent(agent_id)
    print(f"✅ Initialized Formula Provider agent")

    # YoY Analyst
    agent_id = "asst_SboKcNFaQnkxS6k6mDj3GcGT"
    yoy_analyst = await client.agents.get_agent(agent_id)
    print(f"✅ Initialized YoY Analyst agent")


    return [
        # rag_agent,
        metric_retrieval_analyst,
        formula_provider,
        yoy_analyst
    ]

async def main():
    """Main function to run the agents."""
    fin_statement_file = None
    agents = []
    
    # 0. Initialize Agents
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        try:
            kernel = Kernel()
        

            settings = AzureAIAgentSettings(
                model_deployment_name=os.environ.get("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME", ""))
            # Load all predefined agents
            agents = await get_agents(kernel, settings, client)

            # Create group chat with built-in orchestration
            chat_completion_service = AzureChatCompletion(
                deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"), 
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
            )
            print("Available agents:")
            for agent in agents:
                print(f"  - {agent.name}")
            

            manager = StandardMagenticManager(
                chat_completion_service=chat_completion_service
            )
            print(f"Manager created: {type(manager).__name__}")

            magentic_orchestration = MagenticOrchestration(
                members=agents,
                manager=manager,
                agent_response_callback=agent_response_callback,
                streaming_agent_response_callback=streaming_agent_response_callback,
                description="Orchestration of the financial analysis workflow"
            )
            print(f"MagenticOrchestration created with {len(agents)} agents")

            runtime = InProcessRuntime()
            runtime.start()


            orchestration_result = await magentic_orchestration.invoke(
                task=(
                    """

                    Help me to generate a comprehensive Financial Report through Formula Analysis and Year-over-Year (YoY) Analysis processes.
                    Your responsibilities:
                    1. Coordinate the execution of two main analytical workflows:
                    - Formula Analysis Process
                    - Year-over-Year (YoY) Analysis Process
                    2. Synthesize results from specialized agents: RAG_agent, Formula_provider, Metric_retrieval_analyst, and YoY_analyst
                    3. Ensure all agents complete their tasks and integrate results effectively
                    4. Generate final comprehensive Financial Report

                    Workflow coordination details:

                    **Formula Analysis Process:**
                    - Query RAG_agent with company name to identify the corresponding sector
                    - Use sector information to request relevant formulas and variable names from Formula_provider
                    - Retrieve detailed variable information from Metric_retrieval_analyst
                    - Return data to Formula_provider for calculations
                    - Generate Formula Analysis results

                    **Year-over-Year Analysis Process:**
                    - After completing Formula Analysis, retrieve 3-year historical company metrics from Metric_retrieval_analyst
                    - Send data to YoY_analyst to calculate top 10 metrics with changes exceeding 5%
                    - Receive metrics list with corresponding change values
                    - Query RAG_agent to identify root causes for these metric changes
                    - Generate YoY Analysis results

                    **Final Integration:**
                    - Synthesize Formula Analysis and YoY Analysis results
                    - Generate comprehensive Financial Report with actionable insights
                    - Provide confidence levels for all assessments
                    - Handle any errors or exceptions gracefully, ensuring the workflow can recover and continue

                    """
                ),
                runtime=runtime,
            )

            value = await orchestration_result.get()
            print(f"***** Final Result *****\n{value}")

            print("✅ Workflow completed successfully")

            # dump final results to a file under outputs/datetime/financial_analysis_report.md
            output_dir = os.path.join("outputs", datetime.datetime.now().strftime("%Y%m%d_%H%M"))
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, "financial_analysis_report.md")
            with open(output_file_path, "w") as f:
                f.write(f"Financial Analysis Report for Tesco\n")
                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("### Analysis Results:\n")
                f.write(str(value))
                print(f"✅ Report saved to {output_file_path}")
            
            # Stop the runtime when done
            await runtime.stop_when_idle()

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())