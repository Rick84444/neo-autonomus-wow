from typing import Dict, Any

def auto_heal_selector_failure(run_id: str, failed_step: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    old_selector = failed_step.get('params',{}).get('selector','unknown')
    new_step = {"skill":"web","action":"click","params":{"locator_type":"role","locator_value":"primary-submit-button","previous_selector":old_selector}}
    print(f"[{run_id}] Auto-heal selector: {old_selector} -> role=primary-submit-button")
    return new_step
