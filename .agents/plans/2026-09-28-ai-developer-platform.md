## Goal

Build a small production-like developer platform for coding tasks (a "GitHub for coding tasks" slice) on Kubernetes, operated with SRE practices, provisioned with Terraform, shipped with CI/CD — learning each tool by doing. AI agents/subagents come last, as operators on top of the finished platform. You implement everything yourself; this plan is the sequence.

## Success Criteria

- A minimal task-management app (projects + tasks + runs) runs on a local Kubernetes cluster, deployed via a GitOps pipeline, with health checks, metrics, logs, alerts, and an SLO.
- The same app can be reproduced on a managed cloud cluster provisioned with Terraform (remote state, separate dev/prod environments).
- Every phase has a manual "done when" check you can run yourself.
- No AI code is added until the platform fundamentals are boring and repeatable.

## Context And Current Facts

- Your goal (this session): learning-first plan, AI deferred, Kubernetes as the main focus; stack named by you: Kubernetes, SRE, cloud, Terraform, CI/CD, AI agents + subagents later.
- Workspace `/Users/zac/work/kubernates` was empty; I ran `git init` plus `git status` (branch `main`, no commits yet, git 2.50.1). No app code, manifests, or Terraform exist yet.
- External grounding inspected this run: kind install/usage (local clusters via container nodes, `kind create cluster`), Terraform docs (IaC to build/change/version infrastructure), Argo CD overview (declarative GitOps delivery for Kubernetes, Git repo as source of truth, auto/manual sync), Prometheus overview docs (metrics/operations model), GitHub Actions docs (automate CI/CD workflows in-repo).

## Constraints And Non-goals

- Constraints: you do the implementation (I do not scaffold the app); one small app, not a full GitHub clone; Kubernetes is the deepest learning track; AI is explicitly out of scope until the end.
- Non-goals: multi-cloud from day one; running production state inside the cluster; a polished UI; autonomous agents acting on the cluster in early phases.

## Key Decisions

- Local-first, cloud-second: learn Kubernetes locally with kind, then reproduce on one managed cloud cluster. Rejected cloud-first because the local loop is faster/cheaper for learning and the cloud step then becomes "same manifests, new cluster."
- Plain manifests first, templating/GitOps later: `kubectl apply` → versioned manifests in git → GitOps controller (Argo CD) as the only writer. Rejected starting with GitOps on day one because you should feel the pain it removes.
- Terraform owns everything outside the app: cluster, network, managed data services, remote state. Rejected click-ops and in-repo shell scripts for cloud resources.
- CI builds/tests/scans, GitOps deploys: GitHub Actions for continuous integration, Argo CD sync for continuous delivery. Rejected CI-pushed-to-cluster (`kubectl` from CI) as the end state because Git-as-source-of-truth is auditable and roll-backable.
- Metrics before dashboards: Prometheus instrumentation and alert rules first, visualization second. The SRE learning is in RED/USE signals and alert quality, not dashboard quantity.
- Assumptions (reversible, yours to change): one backend language you already know; one relational database as a managed service in cloud and a throwaway container locally; single cloud provider picked at Phase 4 and kept for the whole project.

## Recommended Approach

Seven phases, each ending in a working checkpoint. Commit at each checkpoint (`git log` should read like the phases below). Do not start the next phase until the current "done when" check passes. Keep a `docs/decisions.md` log from Phase 0 — one paragraph per decision — because the SRE/platform learning is in the tradeoffs, not just the YAML.

## Work Plan

**Phase 0 — Foundations (git, app contract, done in days)**
1. Create repo layout: `app/`, `k8s/base/`, `terraform/`, `docs/`.
2. Define the app contract on paper: `Project`, `Task` (todo/doing/done), `Run` (a task execution record). Three REST endpoints minimum plus `/healthz`, `/readyz`, `/metrics`.
3. Write `docs/slo.md` draft: availability + p95 latency targets for one endpoint (you will measure these in Phase 5).
- Done when: contract + SLO draft committed; you can explain every endpoint's success/failure response without code.

**Phase 1 — Minimal app, production-shaped (no cluster yet)**
1. Implement the API with structured JSON logs and a `/metrics` endpoint.
2. Containerize: non-root user, pinned base image, no secrets in image, config via environment.
3. Add unit + contract tests for the task lifecycle; seed script for demo data.
- Done when: `run container → curl /healthz, /readyz → create/complete a task → see one metric increment` all works locally.

**Phase 2 — Kubernetes core (the main track)**
1. Create a local kind cluster; deploy with plain manifests: Deployment, Service, ConfigMap/Secret (Secrets via env, values redacted from logs).
2. Add in order, one commit each: resource requests/limits + probes; HPA on CPU/custom metric; PodDisruptionBudget; NetworkPolicy (default-deny + explicit allows).
3. Practice the failure drills: kill a pod, roll a bad image, roll back; scale to zero and back.
- Done when: killing any pod never drops readiness-gated traffic; `kubectl rollout history` shows the bad revision and the rollback.

**Phase 3 — CI + GitOps delivery**
1. GitHub Actions: on push → lint/test → build image → scan → push with immutable tag (git SHA); on tag → promote staging→prod by updating the git-stored manifest/tag.
2. Install Argo CD pointed at `k8s/`; enable auto-sync on dev, manual sync on prod; CI never talks to the cluster directly.
3. Rehearse: bad commit auto-deploys to dev, is caught, never promoted; prod rollback = git revert + sync.
- Done when: you can narrate the full path `git push → image SHA → dev sync → prod promotion → revert` from the commit log alone.

**Phase 4 — Terraform + cloud reproduction**
1. Terraform: remote state first, then network → managed cluster → managed database; `envs/dev` and `envs/prod` with identical modules, different sizes.
2. Point the Phase 3 pipeline at the cloud cluster; move app secrets to the cloud secret manager; local DB data stays disposable.
3. Tear down dev with `terraform destroy` and rebuild it from scratch.
- Done when: `destroy → apply → Argo CD sync → passing smoke test` reproduces dev with zero manual clicks.

**Phase 5 — SRE: observability, alerts, SLOs**
1. Prometheus scraping app + cluster; alert rules for latency burn, error budget burn, saturation (CPU/memory, DB connections).
2. Centralized logs with request-ID tracing across API → DB; one dashboard per SLO, not per service.
3. Run game days: latency injection, pod kills, DB failover; tune alerts until each page has a runbook line in `docs/runbooks.md`.
- Done when: each SLO in `docs/slo.md` has a live graph, a burn-rate alert, and a runbook entry you have triggered on purpose at least once.

**Phase 6 — Platform slice ("GitHub for coding tasks" MVP)**
1. Extend the Phase 1 API into platform concepts: repositories/projects, task queue with states, run history with logs — still one deployable, no microservice split.
2. Add the thinnest UI or CLI that creates a task, watches its run, and shows the result; every action audited (who/what/when).
3. Harden multi-tenancy basics: authn/authz on every endpoint, per-tenant rate limits, resource quotas per namespace.
- Done when: a second user (a friend or a second account) can sign up, create a project, run a task end-to-end, and only see their own data.

**Phase 7 — AI agents last (operators, not builders)**
1. Read-only agent: it may query metrics/logs/tasks and propose actions, never execute.
2. Scoped actor: one approved action class (e.g. restart a failed run), behind RBAC + audit + human approval.
3. Subagent split: planner, executor, verifier with bounded retries; every action traceable to the Phase 5 observability stack.
- Done when: you can disable the agent path and the platform still fully operates — AI is an operator tier, not load-bearing.

## Validation Plan

- Phase 0: `git log --oneline` shows contract + SLO commits; explain the API contract from memory.
- Phase 1: local container passes `curl /healthz`, task lifecycle, and metric-increment checks.
- Phase 2: pod-kill drill with zero failed readiness-gated requests; `kubectl rollout history` shows rollback.
- Phase 3: trace one SHA from `git log` → image registry → Argo CD sync state → running pods.
- Phase 4: `terraform destroy/apply` rebuilds dev; smoke test passes; `terraform plan` on prod is empty when nothing changed.
- Phase 5: trigger each alert deliberately; confirm notification + runbook + recovery, then silence-to-green.
- Phase 6: second-account end-to-end task run with correct data isolation.
- Phase 7: agent proposes then executes one approved action with full audit trail; kill-switch test passes.

## Risks / Rollback

- Scope creep (building GitHub, not a slice): rollback is Phase 6 descoped to API + CLI, UI deferred.
- Stateful pain in-cluster: rollback is managed data service + disposable local data (Phase 4 rule).
- Alert fatigue from Phase 5: rollback is "page on burn rate only; everything else tickets."
- Premature AI autonomy: rollback is Phase 7 kill-switch — revoke agent RBAC, platform keeps running.
- Largest risk overall is Phase 2→3 (cluster works, delivery is manual snowflake). The validation gate that catches it: the SHA-trace check in Phase 3.

## Open Questions

- Which single cloud provider will you use for Phase 4 (assumption: you pick one and stay; local-only until then)?
- Which backend language will you implement Phase 1 in (assumption: one you already know, so the learning stays on platform tools)?

## Sources

- [kind](https://kind.sigs.k8s.io/)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Argo CD Overview](https://argo-cd.readthedocs.io/en/stable/)
- [Prometheus Overview](https://prometheus.io/docs/introduction/overview/)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
