import asyncio
import json
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, Callable

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from contextlib import contextmanager
import time
metrics = {}

@contextmanager
def trace(name: str):
    start = time.time()
    print(f"\n🚀 START: {name}")

    try:
        yield
        duration = round(time.time() - start, 2)

        metrics[name] = {
            "duration": duration,
            "status": "success"
        }

        print(f"✅ END: {name} ({duration}s)")

    except Exception as e:
        duration = round(time.time() - start, 2)

        metrics[name] = {
            "duration": duration,
            "status": "failed",
            "error": str(e)
        }

        print(f"❌ ERROR in {name}: {e}")
        raise

# ==============================
# 🔥 SIMPLE TRACE (no dependency)
# ==============================
# @contextmanager
# def trace(name: str):
#     start = time.time()
#     print(f"\n🚀 START: {name}")
#     try:
#         yield
#         duration = round(time.time() - start, 2)
#         print(f"✅ END: {name} ({duration}s)")
#     except Exception as e:
#         print(f"❌ ERROR in {name}: {e}")
#         raise

def route_model(prompt: str):
    if len(prompt) < 500:
        return "fast"   # cheap model
    else:
        return "strong" # better model

# ==============================
# 🔥 AGENT WRAPPER
# ==============================
# class AgentWrapper:
#     def __init__(self, name: str, openai_client):
#         self.name = name
#         self.client = openai_client

#     async def run(self, prompt: str) -> Any:
#         with trace(self.name):

#             def invoke():
#                 response = self.client.responses.create(
#                     input=prompt,
#                     extra_body={
#                         "agent_reference": {
#                             "name": self.name,
#                             "type": "agent_reference"
#                         }
#                     }
#                 )
#                 return response.output_text

#             result = await asyncio.to_thread(invoke)

#             # 🔥 Fix double JSON encoding
#             try:
#                 return json.loads(result)
#             except:
#                 return result


# ==============================
# ⚡ CONCURRENT BUILDER
# ==============================
class ConcurrentBuilder:
    def __init__(self):
        self.tasks: Dict[str, Callable] = {}

    def add_task(self, name: str, fn: Callable):
        self.tasks[name] = fn
        return self

    def build(self):
        async def run():
            task_map = {
                name: asyncio.create_task(self._execute(name, fn))
                for name, fn in self.tasks.items()
            }

            results = {}
            for name, task in task_map.items():
                results[name] = await task

            return results

        return run

    async def _execute(self, name, fn):
        with trace(name):
            return await fn()

class AgentWrapper:
    def __init__(self, name, openai_client):
        self.name = name
        self.client = openai_client

    async def run(self, prompt: str):

        model_type = route_model(prompt)

        with trace(f"{self.name} ({model_type})"):

            def invoke():
                return self.client.responses.create(
                    input=prompt,
                    extra_body={
                        "agent_reference": {
                            "name": self.name,
                            "type": "agent_reference"
                        }
                    }
                ).output_text

            result = await asyncio.to_thread(invoke)

            try:
                return json.loads(result)
            except:
                return result

# ==============================
# 🧠 PROMPT BUILDERS
# ==============================
def build_parser_prompt(req):
    return f"""
Parse this CFO requirement into strict JSON:

{req}
"""


def build_analysis_prompt(role, content, requirements):
    return f"""
You are {role}.

Return ONLY JSON.

Content:
{content}

Requirements:
{json.dumps(requirements)}

Output:
- criteria_scores
- strengths
- gaps
- red_flags
- overall_signal
"""


def build_synth_prompt(parsed, analysis):
    return f"""
You are final decision maker.

Return ONLY JSON.

Requirements:
{json.dumps(parsed)}

Analysis:
{json.dumps(analysis)}

"confidence": 0.82
if final["overall_score"] > 85 and final.get("confidence", 1) > 0.8:
decision = "Advance"

Output:
- overall_score (0-100)
- tier (Strong Yes / Yes / Maybe / No)
- decision (Advance / Hold / Reject)
- strengths
- risks
"""


# ==============================
# 🧪 MAIN PROGRAM
# ==============================
async def main():

    # 🔑 Endpoint (IMPORTANT)
    PROJECT_ENDPOINT = os.environ.get(
        "AZURE_AI_PROJECT_ENDPOINT",
        "https://rg-mayuk-agent-demo.services.ai.azure.com/api/projects/proj-default"
    )

    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    with project_client:
        openai_client = project_client.get_openai_client()

        # 🔥 AGENTS
        parser = AgentWrapper("requirement-parser", openai_client)
        bio = AgentWrapper("bio-analyst", openai_client)
        resume = AgentWrapper("resume-analyst", openai_client)
        reference = AgentWrapper("reference-analyst", openai_client)
        synth = AgentWrapper("score-synthesizer", openai_client)

        # 📄 INPUT DATA
        REQUIREMENT = """
CFO role:
- 15+ years leadership
- Global experience
- M&A
- Board exposure
"""

        BIO = "Candidate bio with global finance leadership..."
        RESUME = "Candidate resume showing finance roles..."
        REFERENCE = "Reference feedback strong leadership..."

        # =====================
        # STEP 1 — PARSER
        # =====================
        parsed = await parser.run(build_parser_prompt(REQUIREMENT))

        # =====================
        # STEP 2 — PARALLEL
        # =====================
        concurrent = (
            ConcurrentBuilder()
            .add_task("bio", lambda: safe_run(bio,
                build_analysis_prompt("bio analyst", BIO, parsed)
            ))
            .add_task("resume", lambda: resume.run(
                build_analysis_prompt("resume analyst", RESUME, parsed)
            ))
            .add_task("reference", lambda: reference.run(
                build_analysis_prompt("reference analyst", REFERENCE, parsed)
            ))
            .build()
        )

        analysis = await concurrent()

        # =====================
        # STEP 3 — SYNTHESIS
        # =====================
        final = await synth.run(build_synth_prompt(parsed, analysis))

        print("\n🔥 FINAL OUTPUT:\n")
        print(json.dumps(final, indent=2))

        print("\n📊 METRICS:")
        print(json.dumps(metrics, indent=2))    

async def safe_run(agent, prompt, retries=2):
    for i in range(retries):
        try:
            return await agent.run(prompt)
        except Exception as e:
            print(f"Retry {i+1} for {agent.name}")

    print(f"Fallback triggered for {agent.name}")
    return await agent.run(prompt + "\nBe more accurate.")

# ==============================
# ▶️ RUN
# ==============================
if __name__ == "__main__":
    asyncio.run(main())