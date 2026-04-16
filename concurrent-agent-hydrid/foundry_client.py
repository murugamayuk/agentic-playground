import os
import json
import asyncio
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient

load_dotenv()
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")

if not PROJECT_ENDPOINT:
    raise ValueError("PROJECT_ENDPOINT is not set")



credential = AzureCliCredential()

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)

openai_client = project_client.get_openai_client()


async def call_foundry_agent(agent_name: str, payload: dict):
    prompt = json.dumps(payload, ensure_ascii=False)

    def invoke():
        conversation = openai_client.conversations.create(
            items=[
                {
                    "type": "message",
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        try:
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=prompt,
                extra_body={
                    "agent_reference": {
                        "name": agent_name,
                        "type": "agent_reference",
                    }
                },
            )
            output_text = response.output_text

            try:
                parsed = json.loads(output_text)
            except Exception:
                parsed = output_text

            return {
                "agent": agent_name,
                "output": parsed
            }
        finally:
            try:
                openai_client.conversations.delete(conversation_id=conversation.id)
            except Exception:
                pass

    return await asyncio.to_thread(invoke)