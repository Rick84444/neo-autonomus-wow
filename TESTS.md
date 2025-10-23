# Running tests and starting the server

Quick commands (run from repository root):

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the test suite:

```powershell
pytest -q
```

Start the API server locally (development):

```powershell
python -m uvicorn ewa.server:app --reload
```

Websocket stream path: ws://127.0.0.1:8000/ws/stream/{run_id}
