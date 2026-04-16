import asyncio
from concurrent_builder import ConcurrentBuilder
from foundry_client import call_foundry_agent


async def run_bio(candidate_id, role):
    return await call_foundry_agent("bio-analyst-v2", {
        "candidate_id": candidate_id,
        "role": role
    })


async def run_resume(candidate_id, role):
    return await call_foundry_agent("resume-analyst-v2", {
        "candidate_id": candidate_id,
        "role": role
    })


async def run_reference(candidate_id, role):
    return await call_foundry_agent("reference-analyst-v2", {
        "candidate_id": candidate_id,
        "role": role
    })


async def run_synth(results):
    return await call_foundry_agent("score-synthesizer-v2", {
        "bio": results["bio"],
        "resume": results["resume"],
        "reference": results["reference"]
    })


async def run_workflow(candidate_id: str, role: str):
    concurrent = (
        ConcurrentBuilder()
        .add_task("bio", lambda: run_bio(candidate_id, role))
        .add_task("resume", lambda: run_resume(candidate_id, role))
        .add_task("reference", lambda: run_reference(candidate_id, role))
    )

    results = await concurrent.run()
    final = await run_synth(results)

    return {
        "candidate_id": candidate_id,
        "result": final
    }


if __name__ == "__main__":
   #output = asyncio.run(run_workflow("CC-CFO-01", "CFO"))
    output = asyncio.run(run_workflow("4744211", "Spec-2602-214NA"))
    print(output)