import asyncio
import json
import requests
import websockets
import sys

# Ensure stdout uses UTF-8 so printed Swedish characters are correct on Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    # reconfigure may not be available in some environments; ignore if so
    pass

WS_URL = "ws://127.0.0.1:8001/ws/stream/RUN_PROMPT"
API_URL = "http://127.0.0.1:8001/api/command"
# Log path for a UTF-8-safe demo output
LOG_PATH = "artifacts/ws_demo_clean.log"


async def listen_and_post():
    # Connect websocket listener
    async with websockets.connect(WS_URL) as ws:
        # open a UTF-8 log file and write both to console and file to avoid PowerShell encoding issues
        with open(LOG_PATH, 'w', encoding='utf-8') as lf:
            def log(s: str):
                print(s)
                try:
                    lf.write(s + "\n")
                    lf.flush()
                except Exception:
                    pass

            log("WS: connected")
            # Start poster in executor so it runs concurrently
            loop = asyncio.get_event_loop()

            def do_post():
                payload = {
                    "prompt": "Skaffa 5 SEK i aktier, jurisdiktion SE",
                    "auto_run": True,
                }
                try:
                    r = requests.post(API_URL, json=payload, timeout=10)
                    log(f"POST status: {r.status_code}")
                    try:
                        # write JSON response to log with proper Unicode
                        resp_text = json.dumps(r.json(), ensure_ascii=False, indent=2)
                        log(f"POST response: {resp_text}")
                    except Exception:
                        log("POST response not JSON")
                except Exception as e:
                    log(f"POST failed: {e}")

            post_future = loop.run_in_executor(None, do_post)

            # Read websocket messages until poster finishes and a short grace period
            try:
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=15)
                        log(f"WS MESSAGE: {msg}")
                    except asyncio.TimeoutError:
                        # no messages recently; break if poster done
                        if post_future.done():
                            break
            except websockets.exceptions.ConnectionClosed:
                log("WS: closed")


if __name__ == '__main__':
    asyncio.run(listen_and_post())
