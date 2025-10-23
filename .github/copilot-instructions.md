Short guidance to help AI coding agents be productive in this repository.

Repository snapshot
- Python FastAPI-based autonomous agent orchestration.
- Key packages live under `ewa/` (engine), `skills/` (pluggable skill implementations), and `db/` (simple logging/storage).

What an agent should know (20–50 lines)

1) Big picture
- `ewa/server.py` is the public entrypoint (FastAPI). It accepts commands, routes prompts, constructs plans via `ewa/planner_v3.py`, and executes steps by loading skills from `skills/loader.py`.
- Planner (`ewa/planner_v3.py`) performs compliance checks via `skills/compliance` and emits `plan_steps` describing `{skill, action, params}`.
- Skills are registered via `skills/loader.register()` and discovered at runtime with `skills/loader.get(name)`. Each skill implements `run(action, params, ctx)` and returns a dict result.

2) Developer workflows (how to run/debug)
- Run the server locally using Uvicorn from the repo root: `uvicorn ewa.server:app --reload` (the project uses FastAPI websockets for live updates at `/ws/stream/{run_id}`).
- A lightweight mock API exists under `neo_autonomous_mock/neo_autonomous_mock/server_mock.py` for external integration testing.
- Code-evolution is gated: `skills/code_evolve.py` enforces allowlists and writes backups to `artifacts/backups` before applying edits. `POLICY.require_dual_confirm_finance` controls apply permissions.

3) Conventions & project-specific patterns
- Safe-path allowlisting: file modifications must use paths rooted in `skills/` or `ewa/` (see `_safe_path` in `skills/code_evolve.py`). Never propose edits outside these roots.
- Logging / audit: events are written via `db/fiduciary.log_event` and runs recorded with `db/value.record_run`. Include run_id in ctx where possible (prompts set one in `ewa/prompt_router.route`).
- Policy & gating: central runtime limits live in `ewa/agent_policy.py` (token/time caps, regulated control flags). Planner consults these to decide `go|stop|adjust`.

4) Integration points & important files
- `ewa/prompt_router.py` — lightweight NL-to-mission router; use it to understand parameter extraction (jurisdiction, amount).
- `skills/code_evolve.py` — shows how to safely propose/apply code changes. Use `propose` to show diffs and `apply` only when dual confirmations are present.
- `ewa/safeguard.py` — backup/restore helpers (artifact backups); useful prior to destructive changes.
- `neo_autonomous_mock/neo_autonomous_mock/server_mock.py` — example request/response shapes for planning and execution APIs.

5) Quick examples
- Create a plan: POST /api/command with JSON {"prompt":"Skaffa 1000 SEK i aktier, jurisdiktion SE","auto_run":false} — server will return planner output.
- Read a file safely via `code_evolve` skill: skill `code_evolve.run("read", {"path":"skills/some_skill.py"}, ctx={"run_id":"RUN123"})`.

6) Safety notes for agents
- Never bypass `_safe_path` checks. When proposing code edits, return a unified diff (the code_evolve skill already generates this). When applying changes, create backups and require dual confirmation flags in params.
- Respect `POLICY` caps in `ewa/agent_policy.py`; planner may return `decision: stop` for compliance/high-risk cases.

If anything in this file is unclear or you want more examples (e.g., common skill signatures or db schemas), ask and I'll expand with concrete samples and tests.
