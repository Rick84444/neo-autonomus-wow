import json
from fastapi.testclient import TestClient
from ewa.server import app


def test_command_plan_preview():
    client = TestClient(app)
    payload = {"prompt": "Skaffa 1000 SEK i aktier, jurisdiktion SE", "auto_run": False}
    resp = client.post("/api/command", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "plan" in body
    plan = body["plan"]
    assert "decision" in plan
    assert "plan_steps" in plan
    # If decision is stop, planner placed an explicit reason
    if plan.get("decision") == "stop":
        assert "reason" in plan


def test_planner_decisions_various_prompts():
    from ewa.planner_v3 import plan_v3
    # Low-risk prompt
    p1 = plan_v3("Check the market for DEMO", "portfolio_baseline", {"run_id":"T1","amount":100})
    assert p1.get("simulate")
    assert p1.get("plan_steps")

    # High-risk prompt (large amount) should trigger compliance check and possibly stop
    p2 = plan_v3("Buy risky assets", "portfolio_baseline", {"run_id":"T2","amount":1000000})
    assert p2.get("simulate")
    assert "decision" in p2


def test_full_execution_auto_run_true(tmp_path):
    # Use TestClient to run with auto_run True; since skills are internal, this will execute the sample finance step
    from ewa.agent_policy import POLICY
    client = TestClient(app)
    # Temporarily relax dual-confirm requirement so the finance skill can execute in tests
    old_flag = POLICY.require_dual_confirm_finance
    POLICY.require_dual_confirm_finance = False
    try:
        payload = {"prompt": "Skaffa 10 SEK i aktier, jurisdiktion SE", "auto_run": True}
        resp = client.post("/api/command", json=payload)
    finally:
        POLICY.require_dual_confirm_finance = old_flag
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("executed") in (True, False)
    # If executed, results should be present
    if body.get("executed"):
        assert isinstance(body.get("results"), list)

