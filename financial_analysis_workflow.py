import os
import asyncio
import datetime

from azure.ai.agents.models import FilePurpose
from azure.identity import DefaultAzureCredential
from semantic_kernel.agents import (
    AgentRegistry, AzureAIAgent, AzureAIAgentSettings,
    StandardMagenticManager, Agent,
)
from semantic_kernel.agents.orchestration.magentic import MagenticOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents import StreamingChatMessageContent, ChatMessageContent

# Import and register plugins
from tools.calculator import CalculatorPlugin
from tools.yoy_calculator import YoYCalculatorPlugin
from tools.ai_search import RagPlugin

# load .env variables
from dotenv import load_dotenv
load_dotenv()

is_new_message = True

def streaming_agent_response_callback(message: StreamingChatMessageContent, is_final: bool) -> None:
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
    rag_agent_kernel = Kernel()
    rag_agent_kernel.add_plugin(RagPlugin(), plugin_name="ai_search")
    print("✅ Registered ai_search plugins to kernel")
    rag_agent = await AgentRegistry.create_from_file(
        f"src/agents/declarative/rag_agent.yaml",
        kernel=rag_agent_kernel,
        settings=settings,
        client=client,
    )
    print(f"✅ Initialized RAG Agent agent")

    metric_settings = AzureAIAgentSettings(
        model_deployment_name=settings.model_deployment_name,
        endpoint=settings.endpoint,
        agent_id="asst_V6udTBrczM71JlmWE0MzblsY"
    )
    agent_id = "asst_V6udTBrczM71JlmWE0MzblsY"
    metric_retrieval_analyst_instance = await client.agents.get_agent(agent_id)
    metric_retrieval_analyst_instance.description = "This agent is used to search information from financial data(metrics) in json format, and return the information in json format. The financial data is in the file uploaded to the vector store, containg the financial data for the company Unilever and Tesco across years 2022-2024. The agent will return the metric information in json format."
    metric_retrieval_analyst = AzureAIAgent(
        kernel=kernel,
        settings=metric_settings,
        client=client,
        name="Metric_Retrieval_Analyst",
        definition=metric_retrieval_analyst_instance,
        instructions="""You are a financial data assistant that MUST ALWAYS use the file search tool to retrieve information from the financial_data.json file before providing any response.\n\n                        IMPORTANT: For EVERY user query, you MUST:\n                        1. ALWAYS call the file search tool first to search the financial_data.json file\n                        2. Extract the relevant financial data from the search results\n                        3. Format your response as JSON\n\n                        The output should be in the following format:\n                        {\n                            \"company\": \"Tesco\",\n                            \"year\": \"2024\",\n                            \"financial_metrics\": {\n                                \"metric1\": \"value1\",\n                                \"metric2\": \"value2\"\n                            }\n                        }\n\n                        NEVER provide information without first searching the file. If you cannot find relevant information in the file, return \"No relevant information found\"."""
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
        instructions="""You are a financial data assistant that MUST ALWAYS use the file search tool to retrieve information from the financial_data.json file before providing any response.\n                    \n                        Remember, for every question, you must follow these steps:\n                        1. ALWAYS call the file search tool first to search the key_value.json file\n                        2. Extract the relevant financial data from the search results\n                        3. Only output the direct answer,no more sentences\n                    \n                        NEVER provide information without first searching the file. If you cannot find relevant information in the file, return \"No relevant information found\"."""
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
        instructions="""You are a financial data assistant that MUST ALWAYS use the file search tool to retrieve information from the financial_data.json file before providing any response. \n                        Data Cleansing Instructions:\n                        \n                        1. Remove All Non-Numeric Characters\n                        \n                        Delete currency symbols (e.g., £, $, €), letters, spaces, and other non-numeric characters\n                        \n                        Exception: Preserve commas ,, parentheses ( ), and decimal points .\n                        \n                        Example:\n                        £68,187m → 68,187\n                        $(123.45) → (123.45)\n                        \n                        2. Eliminate Thousand Separators\n                        \n                        Remove all commas (,) used as thousand separators\n                        \n                        Example:\n                        68,187 → 68187\n                        (62,836) → (62836)\n                        \n                        3. Convert Parentheses to Negative Values\n                        \n                        Replace numbers wrapped in parentheses ( ) with negative equivalents:\n                        \n                        Remove parentheses\n                        \n                        Prefix with minus sign -\n                        \n                        Handles space variations automatically\n                        \n                        Example:\n                        (62836) → -62836\n                        ( 123.45 ) → -123.45\n                        \n                        4. Remove all metrics (dictionary entries) that contain any null (empty) values in their year fields\n                        \n                        For example, given json:\n                        {\"Metric\": \"Depreciation\", \"2022\": \"1577\", \"2023\": \"1700\", \"2024\": \"899\"},\n                        {\"Metric\": \"Amortization\", \"2022\": null, \"2023\": \"278\", \"2024\": \"280\"}\n                        \n                        Only keep entries where all year values are not null:\n                        {\"Metric\": \"Depreciation\", \"2022\": \"1577\", \"2023\": \"1700\", \"2024\": \"899\"}\n                        Delete any metric entry that contains null in any year field (e.g., \"2022\", \"2023\", or \"2024\").\n                        \n                        5. After cleansing, call the available calc_yoy tool to calculate the Year-over-Year (YOY) value for each metric using cleansed json data.\n                        \n                        6. Output the json"""
    )
    print(f"✅ Initialized YoY Analyst agent")

    calculation_agent_kernel = Kernel()
    calculation_agent_kernel.add_plugin(CalculatorPlugin(), plugin_name="calculator")
    print("✅ Registered calculator plugins to kernel")
    calculation_agent = await AgentRegistry.create_from_file(
        f"src/agents/declarative/calculation_agent.yaml",
        kernel=calculation_agent_kernel,
        settings=settings,
        client=client,
    )
    print(f"✅ Initialized Calculation Agent")

    report_formating_agent = await AgentRegistry.create_from_file(
        f"src/agents/declarative/report_formating_agent.yaml",
        kernel=kernel,
        settings=settings,
        client=client,
    )
    print(f"✅ Initialized Report_formating_agent Agent")

    return [rag_agent, metric_retrieval_analyst, formula_provider, yoy_analyst, calculation_agent, report_formating_agent]

async def main():
    try:
        creds = DefaultAzureCredential()
        client = AzureAIAgent.create_client(credential=creds)
        
        kernel = Kernel()
        settings = AzureAIAgentSettings(
            model_deployment_name=os.environ.get("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME", ""),
            endpoint=os.environ.get("AZURE_AI_AGENT_ENDPOINT", "")
        )
        agents = await get_agents(kernel, settings, client)

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
            name="Manager",
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
                Help me to generate a comprehensive Financial Report through Formula Analysis and Year-over-Year (YoY) Analysis processes.\n\n                The Company name is \"Tesco\"\n\n                Your responsibilities:\n                1. Coordinate the execution of two main analytical workflows:\n                - Formula Analysis Process\n                - Year-over-Year (YoY) Analysis Process\n                2. Synthesize results from specialized agents: RAG_agent, Formula_provider, Metric_retrieval_analyst, YoY_analyst ,Calculation_agent and Report_formating_agent\n                3. Ensure all agents complete their tasks and integrate results effectively\n                4. After finishing the `Formula Analysis Process` and `ear-over-Year Analysis Process`, send all the result from the these processes to Report_formating_agent for generating final comprehensive Financial Analysis Report\n\n                Workflow coordination details:\n\n                **Formula Analysis Process:**\n                - Query RAG_agent with company name to identify the corresponding sector\n                - After retrieving the sector of this company, manager should send this sector toFormula_provider, and use this sector information to request relevant formulas and variable names from Formula_provider\n                - Retrieve detailed variable information from Metric_retrieval_analyst\n                - Return data to Calculation_agent for calculations\n                - Generate Formula Analysis results\n\n                **Year-over-Year Analysis Process:**\n                - After completing Formula Analysis, retrieve 3-year historical company metrics from Metric_retrieval_analyst\n                - Send data to YoY_analyst get YoY data and calculate top 10 metrics with changes exceeding 5% with the assistance of Calculation_agent\n                - Receive metrics list with corresponding change values from YoY_analyst\n                - Query RAG_agent with the metrics list from YoY_analyst to identify root causes for these metric changes\n                - Generate YoY Analysis results by manager\n\n                **Notice**\n                Assign task to RAG agent only when you are going to identify sector of the company in the fomula process and identify root causes for these metric changes in the YoY process.\n                The report and the summarization task should be finish by the manner as the orchestrator itself.\n\n                Manager should proceed the Formula Analysis workflow and YoY process, NOT the RAG Agent.\n\n                **Final Integration:**\n                - Synthesize Formula Analysis and YoY Analysis results\n                - Generate comprehensive Financial Report with actionable insights\n                - Provide confidence levels for all assessments\n                - Handle any errors or exceptions gracefully, ensuring the workflow can recover and continue\n                """
            ),
            runtime=runtime,
        )

        value = await orchestration_result.get()
        print(f"***** Final Result *****\n{value}")

        print("✅ Workflow completed successfully")

        output_dir = os.path.join("outputs", datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "financial_analysis_report.md")
        with open(output_file_path, "w") as f:
            f.write(f"Financial Analysis Report for Tesco\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("### Analysis Results:\n")
            f.write(str(value))
            print(f"✅ Report saved to {output_file_path}")

        await runtime.stop_when_idle()

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 