from typing import Dict, Any
from .loader import Skill, register

class ComplianceSkill(Skill):
    name = "compliance"
    def health(self) -> bool: 
        return True

    def run(self, action: str, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        if action != "assess":
            raise ValueError("unknown action")

        goal = (params.get("goal") or "").lower()
        juris = (params.get("jurisdiction") or "SE").upper()
        amount = float(params.get("amount") or 0.0)
        kyc = bool(params.get("kyc_verified") or True)

        score = 0.0
        factors = []

        if juris not in ("SE","EU","US","UK"):
            score += 0.4; factors.append("Unknown jurisdiction")
        if amount >= 10000:
            score += 0.3; factors.append("High amount")
        if not kyc:
            score += 0.4; factors.append("KYC missing")
        if any(w in goal for w in ("krypto","crypto","defi")):
            score += 0.2; factors.append("Crypto exposure")

        score = min(1.0, score)
        level = "Low" if score < 0.3 else "Medium" if score < 0.6 else "High"

        return {"ok": True, "jurisdiction": juris, "risk_score": round(score,3), "risk_level": level, "factors": factors or ["None"]}

register(ComplianceSkill())
