from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import time

from ewa.prompt_router import route
from ewa.planner_v3 import plan_v3
from skills.loader import get as get_skill
from db.fiduciary import fetch_logs
from db.value import record_run, optimization_trigger

app = FastAPI(title="Neo Autonomous WOW Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: List[WebSocket] = []

@app.websocket("/ws/stream/{run_id}")
async def websocket_endpoint(ws: WebSocket, run_id: str):
    await ws.accept()
    clients.append(ws)
    try:
        await ws.send_json({"status":"ready","message":f"Ansluten. Körning {run_id}."})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)

async def broadcast(data: Dict[str, Any]):
    dead = []
    for c in clients:
        try: await c.send_json(data)
        except: dead.append(c)
    for d in dead:
        try: clients.remove(d)
        except: pass

class CommandReq(BaseModel):
    prompt: str
    auto_run: bool = True

@app.post("/api/command")
async def api_command(req: CommandReq):
    routed = route(req.prompt)
    plan = plan_v3(routed["goal"], routed["mission_code"], routed["params"])
    if plan.get("decision") != "go" or not req.auto_run:
        return {"plan": plan, "executed": False}
    await broadcast({"status":"running","message":"Exekverar plan…"})
    results, t0 = [], time.time()
    for i, step in enumerate(plan["plan_steps"]):
        await broadcast({"status":"thinking","message":f"Kör {step.get('skill')}.{step.get('action')} ({i+1}/{len(plan['plan_steps'])})"})
        try:
            res = get_skill(step["skill"]).run(step["action"], step.get("params", {}), ctx={"run_id": routed["params"].get("run_id","local")})
            results.append(res)
        except Exception as e:
            # Don't let a failing skill crash the whole server; record the error and continue
            err = {"ok": False, "skill": step.get("skill"), "action": step.get("action"), "error": str(e)}
            results.append(err)
            await broadcast({"status":"error","message":f"Steg {i+1} fel: {e}"})
            # continue to next step
        await broadcast({"status":"success","message":f"Steg {i+1} klart."})
    wall = round(time.time()-t0,2)
    outs = [{"i":i,"skill":s.get("skill"),"action":s.get("action"),"ok":True} for i,s in enumerate(plan.get("plan_steps",[]))]
    # db.value.record_run signature: record_run(run_id: str, est_time_s: float, wall_time_s: float, step_outcomes: list[dict])
    est_time = plan.get("simulate", {}).get("est_time_s", None)
    run_id = routed.get("params", {}).get("run_id", "local")
    record_run(run_id, est_time, wall, outs)
    await broadcast({"status":"done","message":"Klar.", "results": results, "wall": wall})
    if routed["params"].get("optimize", False):
        await broadcast({"status":"thinking","message":"Optimerar mål…"})
        opt = optimization_trigger(routed["goal"], routed["mission_code"], routed["params"], plan, outs, results)
        await broadcast({"status":"done","message":"Optimering klar.", "optimization": opt})
    return {"plan": plan, "executed": True, "results": results, "wall": wall}
