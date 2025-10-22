from typing import Dict, Any
import time

def auto_heal_timeout(run_id: str, failed_step: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    for attempt in range(2):
        delay = 2 ** attempt
        print(f"[{run_id}] TIMEOUT: väntar {delay}s och försöker igen ({attempt+1}/2)…")
        time.sleep(delay)
    return failed_step
