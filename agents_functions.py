# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with custom functions from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_functions.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import os, time, sys
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    FunctionTool,
    ListSortOrder,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
)

current_path = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from user_functions import user_functions
from dotenv import load_dotenv

load_dotenv()

data = """{
  "tesco": [
    {"Metric": "Inventory", "2022": "2339", "2023": "2510", "2024": "2632"},
    {"Metric": "Cash", "2022": "2345", "2023": "2465", "2024": "346"},
    {"Metric": "Marketable_Securities", "2022": "2076", "2023": "1628", "2024": "889"},
    {"Metric": "Accounts_Receivable", "2022": "1263", "2023": "1315", "2024": "576"},
    {"Metric": "Accounts_Payable", "2022": "9234", "2023": "9818", "2024": "-81"},
    {"Metric": "Total_Debt", "2022": "7399", "2023": "7351", "2024": "-7219"},
    {"Metric": "Revenue_a_k_a_Sales", "2022": "61344", "2023": "65762", "2024": "68187"},
    {"Metric": "Cost_of_Goods_Sold_COGS", "2022": "45136", "2023": "48822", "2024": "-62836"},
    {"Metric": "Operating_Income_EBIT", "2022": "2560", "2023": "2509", "2024": "2821"},
    {"Metric": "EBITDA", "2022": "4057", "2023": "4057", "2024": "4362"},
    {"Metric": "Net_Income", "2022": "1483", "2023": "2064", "2024": "1192"},
    {"Metric": "Interest_Expense", "2022": "650", "2023": "373", "2024": "373"},
    {"Metric": "Interest_Income", "2022": "9", "2023": "85", "2024": "94"},
    {"Metric": "Depreciation", "2022": "1577", "2023": "1700", "2024": "899"},
    {"Metric": "Capital_Expenditures_Capex", "2022": "1.1", "2023": "1235", "2024": "1314"},
    {"Metric": "Operating_Cash_Flow", "2022": "4.5", "2023": "3722", "2024": "162"}
  ]
}"""

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Initialize function tool with user functions
functions = FunctionTool(functions=user_functions)


agents_client = project_client.agents

# Create an agent and run user's request with function calls
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="calculator-agent",
    instructions="You are a helpful agent that can perform calculations according to the user's request.",
    tools=functions.definitions,
)
print(f"Created agent, ID: {agent.id}")


thread = agents_client.threads.create()
print(f"Created thread, ID: {thread.id}")

message = agents_client.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"calculate the yoy of tesco from {data} and show the result larger than 5%",
)
print(f"Created message, ID: {message.id}")

run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
print(f"Created run, ID: {run.id}")

while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        if not tool_calls:
            print("No tool calls provided - cancelling run")
            agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
            break

        tool_outputs = []
        for tool_call in tool_calls:
            if isinstance(tool_call, RequiredFunctionToolCall):
                try:
                    print(f"Executing tool call: {tool_call}")
                    output = functions.execute(tool_call)
                    tool_outputs.append(
                        ToolOutput(
                            tool_call_id=tool_call.id,
                            output=output,
                        )
                    )
                except Exception as e:
                    print(f"Error executing tool_call {tool_call.id}: {e}")

        print(f"Tool outputs: {tool_outputs}")
        if tool_outputs:
            agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

    print(f"Current run status: {run.status}")

print(f"Run completed with status: {run.status}")

# Delete the agent when done
agents_client.delete_agent(agent.id)
print("Deleted agent")

# Fetch and log all messages
messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
for msg in messages:
    if msg.text_messages:
        last_text = msg.text_messages[-1]
        print(f"{msg.role}: {last_text.text.value}")
