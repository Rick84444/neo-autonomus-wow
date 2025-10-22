from typing import Dict, Any

def auto_heal_auth(run_id: str, failed_step: Dict[str, Any], error_message: str) -> Dict[str, Any]:
    creds = {"username":"demo_user","password":"demo_pass"}
    steps = [
        {"skill":"web","action":"goto","params":{"url":"https://example.com/login"}},
        {"skill":"web","action":"type","params":{"selector":"#user","value":creds["username"]}},
        {"skill":"web","action":"type","params":{"selector":"#pass","value":creds["password"]}},
        {"skill":"web","action":"click","params":{"selector":"button[type=submit]"}},
        failed_step
    ]
    return {"auto_heal_chain": steps}
