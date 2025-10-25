from typing import Dict

_registry: Dict[str, object] = {}

class Skill:
    name: str = "base"
    def health(self) -> bool: return True
    def run(self, action: str, params: dict, ctx: dict) -> dict: raise NotImplementedError

def register(skill: Skill):
    _registry[skill.name] = skill

def get(name: str) -> Skill:
    s = _registry.get(name)
    if not s:
        # Try to import the skill module dynamically (allow lazy registration)
        try:
            import importlib
            importlib.import_module(f"skills.{name}")
        except Exception:
            pass
        s = _registry.get(name)
    if not s:
        raise KeyError(f"Skill not found: {name}")
    return s
