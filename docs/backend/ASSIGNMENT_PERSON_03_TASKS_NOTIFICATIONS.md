# Backend assignment — Person 3: Tasks & notification foundation

**Owner:** Person 3 (Tasks / notifications)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §12, HLD §3.4, §6 notification design, BACKLOG B8.

**Base in repo:** `apps.tasks` with `Task`, `TaskStatus` / `TaskType`, and `NotificationLog`. Extend via **new migrations**; APIs in `apps/tasks/urls.py`. [`ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md).

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Your app | `backend/apps/tasks/` | **Primary** — models, Celery tasks module (e.g. `tasks/tasks.py` or `apps/tasks/services/`), views, `urls.py`, tests |
| Land | `backend/apps/land/` | FK target `land.LandFile`; reverse `land.tasks` |
| Settings / Celery | `backend/config/settings/base.py`, `config/celery.py` | Beat schedule / imports — coordinate small edits |
| Telemetry | `apps/telemetry/tasks.py` | **Reference only** for Celery style |

### 0.2 Documentation checklist (read before coding)

1. **This entire file.**
2. [`docs/rules.md`](../rules.md) — Celery, notifications, no sync WhatsApp in HTTP.
3. [`docs/PRD.md`](../PRD.md) — tasks / automation.
4. [`docs/HLD.md`](../HLD.md) — §3.4 tasks, §6 notifications.
5. [`docs/backend/ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md) — `tasks` on `LandFile`.
6. [`docs/COMPLETED.md`](../COMPLETED.md), [`docs/BACKLOG.md`](../BACKLOG.md), [`docs/IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md).
7. [`README.md`](../../README.md) — Redis/Celery notes (Path B); Path A uses eager Celery in dev.
8. [`docs/COCKROACHDB_MIGRATIONS.md`](../COCKROACHDB_MIGRATIONS.md) if you add schema.
9. [`docs/DEV_DATABASE.md`](../DEV_DATABASE.md) — if `migrate` fails after pull.

### 0.3 Machine setup: first time and after every `git pull`

```bash
git checkout main && git pull --rebase origin main
cp .env.example .env   # once if needed

cd backend && uv sync --all-groups && uv run python manage.py migrate
cd backend && uv run python manage.py seed_demo_geography   # optional

cd backend && uv run python manage.py runserver 0.0.0.0:8000
```

**If `migrate` fails:** reset local SQLite per **[`docs/DEV_DATABASE.md`](../DEV_DATABASE.md)**.

Before PR: `pnpm install && pnpm check` (optional `pnpm run ci`).

### 0.4 Integration map (Tasks ↔ rest of LIMP)

| Connection | Detail |
|------------|--------|
| **Land** | `Task.land` → `land.LandFile`; `land.tasks`. |
| **Users** | `assigned_to` → `users.User`; scope querysets by assignee. |
| **Legal** | Optional later: Person 1 triggers `send_task_assignment_notification.delay(...)` — keep a **stable function path** documented in your PR. |
| **WhatsApp / SMS** | Stub + `NotificationLog` until Meta/Twilio env vars exist ([`README.md`](../../README.md)). |
| **URLs** | [`apps/tasks/urls.py`](../../backend/apps/tasks/urls.py); included from [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py). |

### 0.5 Code patterns to mirror

[`apps/land/views.py`](../../backend/apps/land/views.py), [`apps/telemetry/tasks.py`](../../backend/apps/telemetry/tasks.py) for `@shared_task` usage.

### 0.6 Local verification

- http://localhost:8000/api/v1/health/
- http://localhost:8000/api/schema/swagger/

---

## 1. Mandatory reading (before you write code)

1. [`docs/rules.md`](../rules.md) — Celery rules (`@shared_task(bind=True, max_retries=3)`), **no synchronous** outbound WhatsApp/SMS in HTTP handlers, soft delete, envelope, RBAC.
2. [`docs/HLD.md`](../HLD.md) §3.4 (task creation flow), §6 (notification retries, logging).
3. [`backend/config/celery.py`](../../backend/config/celery.py) and [`apps/telemetry/tasks.py`](../../apps/telemetry/tasks.py) — existing Celery patterns.
4. [`backend/config/settings/base.py`](../../backend/config/settings/base.py) — `CELERY_BEAT_SCHEDULE` if you add periodic reminders.

---

## 2. Toolchain you must use

| Tool | Requirement |
|------|----------------|
| **Python** | **3.12+** |
| **uv** | `cd backend && uv sync --all-groups`; **`uv run`** for pytest/ruff |
| **Node / pnpm** | **Node 22+**, **pnpm 10** |
| **Git** | Feature branch + PR |

---

## 3. Your scope (what to build)

Work in the **existing** app **`apps.tasks`**.

### 3.1 Task model (foundation)

- **`Task` already exists** with `land`, `title`, `description`, `task_type`, `status`, `due_date`, `assigned_to`. Add fields (e.g. priority, legal-case link) via **new migrations** as needed.
- **Do not** add FK to `legal.LegalCase` in the first PR unless Person 1’s schema is stable on `main`; use **nullable UUID** or `JSONField` metadata (`{"legal_case_id": "..."}`) for cross-module links until both PRs exist, then a follow-up migration can add a real FK.

### 3.2 Notification log

- **`NotificationLog` exists** (channel, phone, user, status, `task` FK, summaries). Extend fields if needed via new migrations.
- Append-only semantics in application code (no hard delete).

### 3.3 Celery tasks (stubs are acceptable for Phase 1)

- `send_task_assignment_notification(self, task_id)` — **idempotent**; for now log and write `NotificationLog` row with status `STUB` or `PENDING` unless Meta/Twilio env vars are set.
- Optional beat job: **daily** overdue task scan — enqueue reminders (stub ok); document env vars required for real sends.

### 3.4 API & RBAC

- CRUD or list/create/update for tasks:
  - Users see **only tasks assigned to them** for operational roles (FIELD_STAFF, surveyors, external advocate if you add task assignment for them).
  - **FOUNDER** / **MANAGEMENT**: see all or per PRD — state choice in PR.
- Use DRF + explicit `get_queryset()`; never rely on frontend hiding data.

Register ViewSets in **`apps/tasks/urls.py`**; it is already wired from [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py).

### 3.5 Tests

- Create task, assign user, assert queryset scoping for two users.
- Celery task called with `.apply()` or test mode (eager) — verify `NotificationLog` row created.
- Unauthorized role cannot read others’ tasks.

---

## 4. Files and directories

### 4.1 You own

- `backend/apps/tasks/**` (already registered in settings and `api_v1_urls`)
- New migrations `0002_…` onward as needed
- Optional: small additions to `CELERY_BEAT_SCHEDULE` in settings (coordinate if merge conflicts — prefer separate schedule key)

### 4.2 You must NOT touch

- `backend/apps/legal/**`, `backend/apps/revenue/**`, `backend/apps/documents/**`
- `frontend/**`

---

## 5. Commands you must run before opening a PR

```bash
cd backend && uv sync --all-groups
cd backend && uv run ruff check .
cd backend && uv run ruff format .
cd backend && uv run pytest -q
```

From **repo root**:

```bash
pnpm install
pnpm check
```

**All must pass before push.** Optional: `pnpm run ci`.

---

## 6. Git workflow (required)

1. `git checkout main && git pull --rebase origin main`
2. `git checkout -b feature/backend-person3-tasks-notifications`
3. Open **PR to `main`**.

---

## 7. Merge / coordination notes

- Person 1 may later call `send_task_assignment_notification.delay(task_id)` from legal signals — expose a stable task API or import path documented in your PR.
- **WhatsApp:** official API only when implemented; stub until credentials exist ([`README.md`](../../README.md) product expectations).

---

*Brief version: April 2026 — Phase 1 foundation.*
