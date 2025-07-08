"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using an asynchronous client.

USAGE:
    python sample_agents_basics_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity aiohttp python-dotenv

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import os
from dotenv import load_dotenv
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.identity.aio import DefaultAzureCredential


async def main() -> None:
    load_dotenv(dotenv_path="config.env")

    # Validate environment variables
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        return

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    agent = None
    thread = None

    try:
        async with project_client:
            agents_client = project_client.agents

            # Create agent
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are a helpful agent"
            )
            print(f"Agent created successfully, Agent ID: asst_62cjkb6GOd6ryvTcFtlcM3EQ")

            # Create conversation thread
            thread = await agents_client.threads.create()
            print(f"Conversation thread created successfully, Thread ID: {thread.id}")

            print("Type 'exit' to end the conversation.")

            while True:
                user_input = input("Your question: ")

                if user_input.lower() == 'exit':
                    break

                # Send user message
                message = await agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_input
                )
                print(f"User message sent, Message ID: {message.id}")

                # Execute agent run
                run = await agents_client.runs.create(
                    thread_id=thread.id,
                    agent_id="asst_62cjkb6GOd6ryvTcFtlcM3EQ"
                )

                # Poll run status until completion
                while run.status in ["queued", "in_progress", "requires_action"]:
                    await asyncio.sleep(1)
                    run = await agents_client.runs.get(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    print(f"Run status: {run.status}")

                # Check run result
                if run.status == "failed":
                    print(f"Run failed: {run.last_error}")
                    continue

                # Retrieve and print the latest assistant response
                assistant_messages = []
                messages = agents_client.messages.list(
                    thread_id=thread.id,
                    order=ListSortOrder.ASCENDING
                )
                async for msg in messages:
                    if msg.role == "assistant":
                        assistant_messages.append(msg)

                if assistant_messages:
                    latest_response = assistant_messages[-1]
                    last_part = latest_response.content[-1]
                    if isinstance(last_part, MessageTextContent):
                        print("Assistant response:")
                        print(f"{last_part.text.value}")
                else:
                    print("No assistant response received")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure resources are cleaned up
        if thread and agent:
            try:
                await project_client.agents.threads.delete(thread.id)
                print(f"Deleted conversation thread: {thread.id}")
            except Exception as e:
                print(f"Failed to delete thread: {e}")

        if agent:
            try:
                await project_client.agents.delete_agent(agent.id)
                print(f"Deleted agent: asst_62cjkb6GOd6ryvTcFtlcM3EQ")
            except Exception as e:
                print(f"Failed to delete agent: {e}")


if __name__ == "__main__":
    asyncio.run(main())
