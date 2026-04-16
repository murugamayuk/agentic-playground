import asyncio
from concurrent_builder import ConcurrentBuilder
from foundry_client import call_foundry_agent




async def run_bio(candidate_id, role):
    return await call_foundry_agent("doc-bio-matching-agent", {
        "candidate_id": candidate_id,
        "role": role
    })


async def run_resume(candidate_id, role):
    return await call_foundry_agent("doc-resume-matching-agent", {
        "candidate_id": candidate_id,
        "role": role
    })


async def run_reference(candidate_id, role):
    return await call_foundry_agent("doc-reference-matching-agent", {
        "candidate_id": candidate_id,
        "role": role
    })


async def run_synth(results, requirements):
    return await call_foundry_agent("match-scoring-agent", {
        "bio": results["bio"],
        "resume": results["resume"],
        "reference": results["reference"],
        "requirements": requirements  # ← ADD THIS
    })


async def run_workflow(candidate_id: str, role: str):
    
    # STEP 0 — extract requirements first (sequential)
    requirements = await call_foundry_agent(
        "requirement-extractor-agent", {
            "candidate_id": candidate_id,
            "role": role
        }
    )
    
    # STEP 1 — concurrent scoring
    concurrent = (
        ConcurrentBuilder()
        .add_task("bio",       lambda: run_bio(candidate_id, role))
        .add_task("resume",    lambda: run_resume(candidate_id, role))
        .add_task("reference", lambda: run_reference(candidate_id, role))
    )
    results = await concurrent.run()
    
    # STEP 2 — synthesize WITH requirements
    final = await run_synth(results, requirements)
    
    return {
        "candidate_id": candidate_id,
        "result": final
    }


if __name__ == "__main__":
   #output = asyncio.run(run_workflow("CC-CFO-01", "CFO"))
    output = asyncio.run(run_workflow("4744211", "Spec-2602-214NA"))
    print(output)
