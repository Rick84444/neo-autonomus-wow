import os
import sys

# Ensure repository root is on sys.path so tests can import ewa, skills, db, etc.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import all skills so they register themselves into skills.loader registry
skills_dir = os.path.join(ROOT, "skills")
if os.path.isdir(skills_dir):
    for fn in os.listdir(skills_dir):
        if fn.endswith('.py') and not fn.startswith('__'):
            mod_name = f"skills.{fn[:-3]}"
            try:
                __import__(mod_name)
            except Exception:
                # allow import errors to surface during tests when they matter
                pass
