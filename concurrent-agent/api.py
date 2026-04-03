from fastapi import FastAPI
from pydantic import BaseModel

# import your existing workflow
from main import run_workflow   # 👈 you rename your function

app = FastAPI()


# request schema (very important for API clarity)
class EvaluateRequest(BaseModel):
    candidate_id: str
    role: str = "CFO"


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    result = run_workflow(
        candidate_id=req.candidate_id,
        role=req.role
    )
    return result
