uvicorn server:app --reloaduvicorn server:app --reloadimport os, json, time
BASE = os.path.join(os.path.dirname(__file__), "..", "artifacts", "value")
os.makedirs(BASE, exist_ok=True)
RUNS = os.path.join(BASE, "runs.json")
FAIL = os.path.join(BASE, "fail_counts.json")

def _load(p, default):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except Exception: return default

def _save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: json.dump(obj,f,ensure_ascii=False,indent=2)

def record_run(run_id: str, est_time_s: float, wall_time_s: float, step_outcomes: list[dict]):
    runs = _load(RUNS, [])
    runs.append({"t":time.time(),"run_id":run_id,"est":est_time_s,"wall":wall_time_s,"steps":step_outcomes})
    _save(RUNS, runs)
    fc = _load(FAIL, {})
    for s in step_outcomes:
        key = f"{s.get('skill')}.{s.get('action')}"
        if not s.get("ok"):
            fc[key] = fc.get(key,0) + 1
        else:
            fc[key] = 0
    _save(FAIL, fc)

def optimization_trigger(est_time_s: float, wall_time_s: float, step_outcomes: list[dict]) -> dict | None:
    if est_time_s and wall_time_s >= est_time_s * 1.5:
        return {"mission":"code_patch_optimize_efficiency",
                "target_path":"skills/web.py",
                "hint":"Minska latens i screenshot"}
    fc = _load(FAIL, {})
    for s in step_outcomes:
        key=f"{s.get('skill')}.{s.get('action')}"
        if fc.get(key,0) >= 3:
            return {"mission":"code_patch_strengthen_skill",
                    "target_path":"skills/web.py",
                    "hint":f"Stabilize {key}"}
    return None
