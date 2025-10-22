import time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Neo Autonomous Mock API")

@app.get("/")
def root():
    return {"status": "online", "timestamp": time.strftime("%H:%M:%S")}

class PlanReq(BaseModel):
    goal: str
    mission_code: str
    params: dict = {}

@app.post("/api/plan_v3")
def plan(req: PlanReq):
    return {
        "decision": "go",
        "simulate": {
            "est_cost_tokens": 12345,
            "est_time_s": 12.3,
            "risk": "green",
            "causal_prediction": {
                "risk_type": "None",
                "consequence": "Ingen betydande risk upptäckt.",
                "mitigation": "N/A"
            }
        },
        "plan_steps": [
            {"skill": "web", "action": "goto", "params": {"url": "https://example.com"}},
            {"skill": "api", "action": "call", "params": {"endpoint": "health"}}
        ]
    }

class ExecReq(BaseModel):
    run_id: str
    plan_steps: list

@app.post("/api/exec")
def exec(req: ExecReq):
    return {
        "status": "succeeded",
        "artefacts": ["/artifacts/demo_report.pdf"],
        "lessons": ["OK"]
    }
