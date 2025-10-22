from typing import Dict, Any, TypedDict
from ewa.agent_policy import POLICY
from skills.loader import get as get_skill
from db.fiduciary import log_event

class CausalPrediction(TypedDict):
    risk_type: str
    consequence: str
    mitigation: str
    compliance: Dict[str, Any]

def self_reflect_on_consequences(goal: str) -> Dict[str, str]:
    s = goal.lower()
    if "web" in s or "sök" in s or "search" in s:
        return {"risk_type":"Data Integrity","consequence":"Källa kan vara föråldrad","mitigation":"Freshness-check på källor"}
    return {"risk_type":"None","consequence":"Standard felhantering","mitigation":"N/A"}

def _simulate(goal: str) -> Dict[str, Any]:
    tokens = 25000 if len(goal) > 50 else 10000
    seconds = 180 if tokens > 20000 else 90
    risk = "yellow" if ("api" in goal.lower() or "code" in goal.lower()) else "green"
    return {"est_cost_tokens": tokens, "est_time_s": seconds, "risk": risk}

def _decide(sim: Dict[str, Any]) -> str:
    if sim["est_cost_tokens"] > POLICY.cost_cap_tokens: return "stop"
    if sim["est_time_s"] > POLICY.time_cap_s: return "adjust"
    if sim["risk"] == "red": return "adjust"
    return "go"

def _assess_compliance(goal:str, params:Dict[str,Any])->Dict[str,Any]:
    return get_skill("compliance").run("assess", {
        "goal": goal,
        "jurisdiction": params.get("jurisdiction","SE"),
        "amount": params.get("amount", 0),
        "kyc_verified": params.get("kyc_verified", True),
    }, ctx={})

def plan_v3(goal: str, mission_code: str, params: Dict[str, Any]) -> Dict[str, Any]:
    sim = _simulate(goal)
    cp = self_reflect_on_consequences(goal)
    comp = _assess_compliance(goal, params)
    sim["causal_prediction"] = {**cp, "compliance": comp}

    log_event("planner","compliance_assess", comp.get("risk_level","?"),
              {"goal":goal,"mission":mission_code,"params":params,"compliance":comp},
              run_id=params.get("run_id","local"))

    if POLICY.regulated_control and comp.get("risk_level") == "High":
        log_event("planner","verdict","stop",{"reason":"Compliance High","compliance":comp}, run_id=params.get("run_id","local"))
        return {"mission": mission_code, "kpi_target": "compliance_block",
                "simulate": sim, "decision": "stop",
                "reason": "Compliance High: " + ", ".join(comp.get("factors",[])),
                "plan_steps": []}

    # Minimal fake plan steps (demo). Replace with LLM-backed planner.
    steps = [
        {"skill":"finance","action":"preview","params":{"api":"broker_demo","symbol":"DEMO","amount": params.get("amount",0),"side":"buy"}},
    ] if mission_code == "portfolio_baseline" else [
        {"skill":"finance","action":"quote","params":{"api":"broker_demo","symbol":"DEMO"}},
    ]

    verdict = _decide(sim)
    return {"mission": mission_code, "kpi_target": "artifact_path",
            "simulate": sim, "decision": verdict, "plan_steps": steps}
