import os, json, sqlite3, time
DB_PATH = os.path.join(os.path.dirname(__file__), "fiduciary.sqlite3")

def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL NOT NULL,
        run_id TEXT,
        actor TEXT,
        action TEXT,
        decision TEXT,
        payload TEXT
    )""")
    return c

def log_event(actor: str, action: str, decision: str, payload: dict, run_id: str|None=None):
    with _conn() as c:
        c.execute("INSERT INTO logs(ts,run_id,actor,action,decision,payload) VALUES(?,?,?,?,?,?)",
                  (time.time(), run_id or "local", actor, action, decision, json.dumps(payload, ensure_ascii=False)))
        c.commit()

def fetch_logs(limit: int=50) -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT id,ts,run_id,actor,action,decision,payload FROM logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    out=[]
    for i,ts,run_id,actor,action,decision,payload in rows:
        try: data=json.loads(payload)
        except: data={"raw":payload}
        out.append({"id":i,"ts":ts,"run_id":run_id,"actor":actor,"action":action,"decision":decision,"payload":data})
    return out
