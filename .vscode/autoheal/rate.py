from typing import Dict, Any
import time, random

def auto_heal_rate(run_id: str, failed_step: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    wait = random.uniform(3,7)
    print(f"[{run_id}] 429 Rate-Limit: väntar {wait:.1f}s innan nytt försök.")
    time.sleep(wait)
    failed_step.setdefault("params",{})["retry_flag"]=True
    return failed_step
