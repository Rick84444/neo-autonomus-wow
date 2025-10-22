from typing import Dict, Any
from .loader import Skill, register
import os, difflib, time, json
from ewa.agent_policy import POLICY
from db.fiduciary import log_event

SAFE_ROOTS = ("skills", "ewa")
BACKUP_DIR = os.path.join("artifacts", "backups")

def _safe_path(p: str) -> str:
    p = os.path.normpath(p).replace("\\","/")
    if not any(p.startswith(r + "/") or p == r for r in SAFE_ROOTS):
        raise PermissionError("Path not allowlisted")
    return p

def _read(p: str) -> str:
    with open(p, "r", encoding="utf-8") as f: return f.read()

def _write(p: str, content: str):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)

def _diff(old: str, new: str, p: str) -> str:
    return "".join(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=p + " (old)",
        tofile=p + " (new)",
        n=3
    ))

class CodeEvolveSkill(Skill):
    name = "code_evolve"

    def health(self) -> bool: return True

    def run(self, action: str, params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        if action == "read":
            target = _safe_path(params["path"])
            return {"ok": True, "path": target, "content": _read(target)}

        if action == "propose":
            target = _safe_path(params["path"])
            new_content = params["new_content"]
            old = _read(target)
            udiff = _diff(old, new_content, target)
            return {"ok": True, "path": target, "diff": udiff, "preview_only": True}

        if action == "apply":
            if POLICY.require_dual_confirm_finance and not (params.get("user_confirm") and params.get("second_confirm")):
                raise PermissionError("Dual confirmation required")
            target = _safe_path(params["path"])
            new_content = params["new_content"]
            old = _read(target)
            udiff = _diff(old, new_content, target)
            os.makedirs(BACKUP_DIR, exist_ok=True)
            ts = int(time.time())
            backup_path = os.path.join(BACKUP_DIR, f"{target.replace('/','__')}.{ts}.bak")
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            _write(backup_path, old)
            _write(target, new_content)
            meta = {"path": target, "backup": backup_path, "ts": ts, "lines": len(new_content.splitlines())}
            with open(os.path.join(BACKUP_DIR, "last_apply.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            log_event("code_evolve","apply","ok",{"path":target,"backup":backup_path,"lines":len(new_content.splitlines())}, run_id=(ctx or {}).get("run_id","local"))
            return {"ok": True, "applied": True, "path": target, "backup": backup_path, "diff": udiff}

        if action == "rollback":
            b = params["backup_path"]
            with open(b,"r",encoding="utf-8") as f: _write(_safe_path(params["path"]), f.read())
            log_event("code_evolve","rollback","ok",{"path":params["path"],"backup":b}, run_id=(ctx or {}).get("run_id","local"))
            return {"ok": True, "rolled_back": True}

        raise ValueError("unknown action")

register(CodeEvolveSkill())
