from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 👇 Your request model
class EvaluateRequest(BaseModel):
    candidate_id: str
    role: str

# 👇 Your existing agent logic (wrap it in a function)
def run_agents(candidate_id: str, role: str):
    # 👉 MOVE your current logic here
    # (bio, resume, reference, scoring)
    
    return {
        "candidate_id": candidate_id,
        "status": "processed"
    }

# 👇 API endpoint
@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    result = run_agents(req.candidate_id, req.role)
    return result


# 👇 THIS is the missing piece
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)