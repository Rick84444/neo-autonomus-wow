from typing import Dict, Any
from .loader import Skill, register
from ewa.agent_policy import POLICY
from db.fiduciary import log_event

class FinanceSkill(Skill):
    name = "finance"
    def health(self) -> bool: return True

    def run(self, action: str, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        run_id = (ctx or {}).get("run_id","local")
        api = params.get("api","broker_demo")
        symbol = params.get("symbol","DEMO")
        amount = float(params.get("amount",0))
        side = params.get("side","buy")

        if action == "preview":
            quote = {"symbol":symbol, "px":123.45, "notional":amount, "side":side, "fees_est": round(amount*0.001,2)}
            log_event("finance","preview","info",{"api":api, **quote}, run_id)
            return {"ok": True, "preview": quote, "confirm_required": True}

        if POLICY.require_dual_confirm_finance:
            if not (params.get("user_confirm") and params.get("second_confirm")):
                log_event("finance","execute","blocked",{"reason":"dual_confirm_missing","api":api,"symbol":symbol,"amount":amount,"side":side}, run_id)
                raise PermissionError("Dual confirmation required")

        if api not in POLICY.allowed_finance_apis:
            log_event("finance","execute","blocked",{"reason":"api_not_allowlisted","api":api}, run_id)
            raise PermissionError("Finance API not allowlisted")

        if action == "paper_trade":
            res={"ok": True, "trade_id": "DEMO123", "status": "placed", "symbol":symbol, "amount":amount, "side":side, "source": api}
            log_event("finance","paper_trade","ok",res, run_id); return res

        if action == "quote":
            res={"ok": True, "symbol": symbol, "price": 123.45, "source": api}
            log_event("finance","quote","ok",res, run_id); return res

        raise ValueError("unknown finance action")

register(FinanceSkill())
