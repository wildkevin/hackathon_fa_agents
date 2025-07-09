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

    rag_agent = await AgentRegistry.create_from_file(
        f"src/agents/declarative/rag_agent.yaml",
        kernel=kernel,
        settings=settings,
        client=client,
    )
    print(f"✅ Initialized RAG Agent agent")

    # rag_agent_settings = AzureAIAgentSettings(
    #     model_deployment_name=settings.model_deployment_name,
    #     endpoint=settings.endpoint,
    #     agent_id="asst_pX3PqWDGsFvZ7bZvLkqh3Q3a"
    # )
    # agent_id = "asst_pX3PqWDGsFvZ7bZvLkqh3Q3a"
    # rag_agent_instance = await client.agents.get_agent(agent_id)
    # rag_agent_instance.description = "This agent is a Rag Agent that can answer questions based on the company information by using azure index browser tool"
    # rag_agent = AzureAIAgent(
    #     kernel=kernel,
    #     settings=rag_agent_settings,
    #     client=client,
    #     name="RAG_Agent",
    #     definition=rag_agent_instance,
    #     instructions="""This agent is a Rag Agent that can answer questions based on the company information by using azure index browser tool"""
    # )
    # print(f"✅ Initialized RAG Agent agent")
    

    metric_settings = AzureAIAgentSettings(
        model_deployment_name=settings.model_deployment_name,
        endpoint=settings.endpoint,
        agent_id="asst_V6udTBrczM71JlmWE0MzblsY"
    )
    # agent_id = "asst_v6rsuv5M4G26vKwD1Cio6cOd"

    agent_id = "asst_V6udTBrczM71JlmWE0MzblsY"
    metric_retrieval_analyst_instance = await client.agents.get_agent(agent_id)
    metric_retrieval_analyst_instance.description = "This agent is used to search information from financial data(metrics) in json format, and return the information in json format. The financial data is in the file uploaded to the vector store, containg the financial data for the company Unilever and Tesco across years 2022-2024. The agent will return the metric information in json format."
    metric_retrieval_analyst = AzureAIAgent(
        kernel=kernel,
        settings=metric_settings,
        client=client,
        name="Metric_Retrieval_Analyst",
        definition=metric_retrieval_analyst_instance,
        instructions="""You are a financial data assistant that MUST ALWAYS use the file search tool to retrieve information from the financial_data.json file before providing any response.

                        IMPORTANT: For EVERY user query, you MUST:
                        1. ALWAYS call the file search tool first to search the financial_data.json file
                        2. Extract the relevant financial data from the search results
                        3. Format your response as JSON

                        The output should be in the following format:
                        {
                            "company": "Tesco",
                            "year": "2024",
                            "financial_metrics": {
                                "metric1": "value1",
                                "metric2": "value2"
                            }
                        }

                        NEVER provide information without first searching the file. If you cannot find relevant information in the file, return "No relevant information found"."""
    )
    print(f"✅ Initialized Metric Retrieval Analyst agent")

    formula_provider_settings = AzureAIAgentSettings(
        model_deployment_name=settings.model_deployment_name,
        endpoint=settings.endpoint,
        agent_id="asst_62cjkb6GOd6ryvTcFtlcM3EQ"
    )
    agent_id = "asst_62cjkb6GOd6ryvTcFtlcM3EQ"
    formula_provider_instance = await client.agents.get_agent(agent_id)
    formula_provider_instance.description = "An Agent to provide formulas and variable names. And calculate the values of the formulas once the value of the variable are provided"
    formula_provider = AzureAIAgent(
        kernel=kernel,
        settings=formula_provider_settings,
        client=client,
        name="Formula_Provider",
        definition=formula_provider_instance,
        instructions="""You are a financial data assistant that MUST ALWAYS use the file search tool to retrieve information from the financial_data.json file before providing any response.
                    
                        Remember, for every question, you must follow these steps:
                        1. ALWAYS call the file search tool first to search the key_value.json file
                        2. Extract the relevant financial data from the search results
                        3. Only output the direct answer,no more sentences
                    
                        NEVER provide information without first searching the file. If you cannot find relevant information in the file, return "No relevant information found"."""
    )
    print(f"✅ Initialized Formula Provider agent")

    yoy_analyst_settings = AzureAIAgentSettings(
        model_deployment_name=settings.model_deployment_name,
        endpoint=settings.endpoint,
        agent_id="asst_SboKcNFaQnkxS6k6mDj3GcGT"
    )
    agent_id = "asst_SboKcNFaQnkxS6k6mDj3GcGT"
    yoy_analyst_instance = await client.agents.get_agent(agent_id)
    yoy_analyst_instance.description = "An Agent to calculate the year-over-year (YoY) analysis of the metrics"
    yoy_analyst = AzureAIAgent(
        kernel=kernel,
        settings=yoy_analyst_settings,
        client=client,
        name="YoY_Analyst",
        definition=yoy_analyst_instance,
        instructions="""You are a financial data assistant that MUST ALWAYS use the file search tool to retrieve information from the financial_data.json file before providing any response. 
                        Data Cleansing Instructions:
                        
                        1. Remove All Non-Numeric Characters
                        
                        Delete currency symbols (e.g., £, $, €), letters, spaces, and other non-numeric characters
                        
                        Exception: Preserve commas ,, parentheses ( ), and decimal points .
                        
                        Example:
                        £68,187m → 68,187
                        $(123.45) → (123.45)
                        
                        2. Eliminate Thousand Separators
                        
                        Remove all commas (,) used as thousand separators
                        
                        Example:
                        68,187 → 68187
                        (62,836) → (62836)
                        
                        3. Convert Parentheses to Negative Values
                        
                        Replace numbers wrapped in parentheses ( ) with negative equivalents:
                        
                        Remove parentheses
                        
                        Prefix with minus sign -
                        
                        Handles space variations automatically
                        
                        Example:
                        (62836) → -62836
                        ( 123.45 ) → -123.45
                        
                        4. Remove all metrics (dictionary entries) that contain any null (empty) values in their year fields
                        
                        For example, given json:
                        {"Metric": "Depreciation", "2022": "1577", "2023": "1700", "2024": "899"},
                        {"Metric": "Amortization", "2022": null, "2023": "278", "2024": "280"}
                        
                        Only keep entries where all year values are not null:
                        {"Metric": "Depreciation", "2022": "1577", "2023": "1700", "2024": "899"}
                        Delete any metric entry that contains null in any year field (e.g., "2022", "2023", or "2024").
                        
                        5. After cleansing, call the available calc_yoy tool to calculate the Year-over-Year (YOY) value for each metric using cleansed json data.
                        
                        6. Output the json"""
    )
    print(f"✅ Initialized YoY Analyst agent")

    calculation_agent_settings = AzureAIAgentSettings(
        model_deployment_name=settings.model_deployment_name,
        endpoint=settings.endpoint,
        agent_id="asst_eV7zxBynDQZZmATc3oHMT2Bd"
    )
    
    # agent_id = "asst_Gb5TwOb7KQRvzVMNUfmjcM52"
    agent_id = "asst_eV7zxBynDQZZmATc3oHMT2Bd"
    # agent_id = "asst_N2DN2siAYBkhtE88VAerU6IB"
    calculation_agent_instance = await client.agents.get_agent(agent_id)
    calculation_agent_instance.description = "a helpful calculation agent that can perform calculations according to the user's request."
    calculation_agent = AzureAIAgent(
        kernel=kernel,
        settings=calculation_agent_settings,
        client=client,
        name="Calculation_Agent",
        definition=calculation_agent_instance,
        instructions="You are a helpful agent that can perform calculations according to the variables in user's request by using tools."
    )
    print(f"✅ Initialized Calculation Agent")

    return [rag_agent, metric_retrieval_analyst, formula_provider, yoy_analyst, calculation_agent]


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
                print(f"  - {agent.name}- {agent.id}")
            

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

                    The Company name is "Tesco"

                    Your responsibilities:
                    1. Coordinate the execution of two main analytical workflows:
                    - Formula Analysis Process
                    - Year-over-Year (YoY) Analysis Process
                    2. Synthesize results from specialized agents: RAG_agent, Formula_provider, Metric_retrieval_analyst, YoY_analyst and Calculation_agent
                    3. Ensure all agents complete their tasks and integrate results effectively
                    4. Generate final comprehensive Financial Report

                    Workflow coordination details:

                    **Formula Analysis Process:**
                    - Query RAG_agent with company name to identify the corresponding sector
                    - Use sector information to request relevant formulas and variable names from Formula_provider
                    - Retrieve detailed variable information from Metric_retrieval_analyst
                    - Return data to Calculation_agent for calculations
                    - Generate Formula Analysis results

                    **Year-over-Year Analysis Process:**
                    - After completing Formula Analysis, retrieve 3-year historical company metrics from Metric_retrieval_analyst
                    - Send data to YoY_analyst get YoY data and calculate top 10 metrics with changes exceeding 5% with the assistance of Calculation_agent
                    - Receive metrics list with corresponding change values
                    - Query RAG_agent with the metrics list from the last step to identify root causes for these metric changes
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