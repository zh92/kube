# kube platform project — handoff

Repo: /Users/zac/work/kubernates, GitHub: zh92/kube (branch main, in sync).
Plan: .agents/plans/2026-09-28-ai-developer-platform.md (7 phases, AI deferred to Phase 7).

## Working style (user constraints, remain active)
- Learning-first: user types the code, assistant guides step by step. Explain BEFORE giving commands. Keep steps tiny (one slice at a time), brief explanations first when asked.
- User corrects course readily; obey latest direction over plan order.

## Stack decisions
- Python, stdlib only (http.server + json). No frameworks, no external deps, no venv. User rejected fastapi/uvicorn.
- unittest (stdlib) for tests: app/test_main.py, run via `python3 -m unittest test_main` from app/.
- SSH to GitHub works via macOS agent (key is passphrase-protected; user runs ssh-add themselves).

## Progress (verified in git)
- e70bcf4 plan, 30c5b5c app v1 (tasks CRUD-lite, /healthz, /readyz, 404/422 handling), 7723454 file persistence (tasks.json, atomic tmp+rename write, missing→empty, corrupt→raise).
- Next up: containerize (app/Dockerfile, build/run, tasks.json volume mount). Frontend explicitly deferred to Phase 6.
