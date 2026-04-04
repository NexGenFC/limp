# Backend assignment — Person 1: Legal & litigation module

**Owner:** Person 1 (Legal)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §3–4, PRD legal sections, [`docs/HLD.md`](../HLD.md) §3.2–3.4, §4 (ERD), §7 (RBAC).

**Base in repo:** `apps.legal` with `LegalCase` (`land` FK) and `0001_initial`. Extend with **new migrations** only; wire APIs in `apps/legal/urls.py`. Map: [`ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md).

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Django project | `backend/config/` | Rarely (`api_v1_urls.py` already includes `apps.legal.urls`) |
| Your app | `backend/apps/legal/` | **Primary** — models, serializers, views, `urls.py`, `tests/` |
| Land anchor | `backend/apps/land/` | Read-only reference; FK target `land.LandFile` |
| Users / RBAC | `backend/apps/users/` | Read patterns; optional new classes in `permissions.py` |
| Product docs | `docs/` | Read; do not skip `rules.md` |

### 0.2 Documentation checklist (read before coding)

1. **This entire file** (scope, commands, Git, coordination).
2. [`docs/rules.md`](../rules.md) — soft delete, RBAC on API, envelope, no disk uploads (use `s3_key`; presign is Person 4).
3. [`docs/PRD.md`](../PRD.md) — legal / litigation requirements.
4. [`docs/HLD.md`](../HLD.md) — §3.2–3.4 legal flow, §7 RBAC, compliance / POA.
5. [`docs/backend/ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md) — `legal_cases` reverse name on `LandFile`.
6. [`docs/COMPLETED.md`](../COMPLETED.md), [`docs/BACKLOG.md`](../BACKLOG.md), [`docs/IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md).
7. [`README.md`](../../README.md) — Path A, CORS, `pnpm check`.
8. [`docs/COCKROACHDB_MIGRATIONS.md`](../COCKROACHDB_MIGRATIONS.md) — before adding unusual constraints.
9. [`docs/DEV_DATABASE.md`](../DEV_DATABASE.md) — if `migrate` fails after pull.

### 0.3 Machine setup: first time and after every `git pull`

```bash
git checkout main && git pull --rebase origin main
cp .env.example .env   # once, if you have no .env

cd backend && uv sync --all-groups && uv run python manage.py migrate
cd backend && uv run python manage.py seed_demo_geography   # optional; land form

cd backend && uv run python manage.py runserver 0.0.0.0:8000
```

**If `migrate` fails:** your `backend/db.sqlite3` was built before the current migration history on `main` (e.g. UUIDv7 on domain tables). **Delete it** and run `migrate` again — reason + commands: **[`docs/DEV_DATABASE.md`](../DEV_DATABASE.md)**.

**Quality gate before PR:** from repo root, `pnpm install && pnpm check` (optional `pnpm run ci`).

### 0.4 Integration map (Legal ↔ rest of LIMP)

| Connection | Detail |
|------------|--------|
| **Land master** | Every new model that “belongs to a parcel” uses FK **`land`** → `land.LandFile` (`PROTECT`). From land: `land.legal_cases`. |
| **Users / advocates** | Assign cases to `users.User`; filter querysets for `EXTERNAL_ADVOCATE` vs in-house per PRD. |
| **Documents** | Store **`s3_key`** on legal artifacts until Person 4’s presign flow is stable; optional FK to `documents.DocumentVersion` in a **later** migration. |
| **Tasks / notifications** | POA reminders may call Person 3’s Celery API after their PR lands; stub or TODO in your PR if needed. |
| **URLs** | Register **`DefaultRouter`** in [`backend/apps/legal/urls.py`](../../backend/apps/legal/urls.py) only — already included from [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py). |

### 0.5 Code patterns to mirror

- [`apps/land/views.py`](../../backend/apps/land/views.py) — `get_queryset`, `perform_create` / `perform_update`, `soft_delete` on destroy.
- [`apps/land/serializers.py`](../../backend/apps/land/serializers.py) — explicit fields.
- [`apps/users/permissions.py`](../../backend/apps/users/permissions.py) — `LandPermission` style.

### 0.6 Local verification

- http://localhost:8000/api/v1/health/
- http://localhost:8000/api/schema/swagger/ — your routes appear after you register the router.

---

## 1. Mandatory reading (before you write code)

1. [`docs/rules.md`](../rules.md) — non-negotiables: soft delete only, RBAC on API, envelope responses, `AuditedModel` / `SoftDeleteModel`, no local file storage for production uploads (store `s3_key` strings; actual pre-sign is Person 4).
2. [`docs/HLD.md`](../HLD.md) — legal case + hearing flow, compliance (Plan of Action / POA before hearing).
3. [`backend/apps/land/`](../../backend/apps/land/) — how `LandFile` and geography FKs are modelled; your models **must** link to land via FK named `land` per `rules.md`.
4. [`backend/apps/users/models.py`](../../backend/apps/users/models.py) — `UserRole` enum; [`permissions.py`](../../backend/apps/users/permissions.py) — pattern for new permission classes.

---

## 2. Toolchain you must use

| Tool | Requirement |
|------|----------------|
| **Python** | **3.12+** (see `backend/pyproject.toml` `requires-python`) |
| **uv** | Install from [astral-sh/uv](https://github.com/astral-sh/uv). Dependencies: `cd backend && uv sync --all-groups` |
| **Node / pnpm** | **Node 22+**, **pnpm 10** (root `package.json` `packageManager`: `pnpm@10.33.0`) — required to run the **same checks as CI** from repo root |
| **Git** | Feature branch + PR (see §7) |

Do **not** use a global `pip install` for project deps; use **`uv run`** so the lockfile (`backend/uv.lock`) stays authoritative.

---

## 3. Your scope (what to build)

Work in the **existing** app **`apps.legal`** (already in `INSTALLED_APPS` and `api_v1_urls`).

### 3.1 Data model (minimum for Phase 1 foundation)

**`LegalCase` already exists** — add normalized models (all on `BaseModel` / audited / soft-delete per existing `apps.core.models`):

- **Legal case** — extend `LegalCase` with fields aligned with the client brief: party role, court jurisdiction, case type (OS, MFA, WP, …), current stage, next hearing date (on case **or** derive from hearings — document choice).
- **Case ↔ advocate** assignment (in-house + external users); external advocates must be scopeable later via JWT `case_ids` (HLD) — for now, enforce **queryset filtering** in `get_queryset`: external advocate sees **only** cases where they are assigned.
- **Hearing** records per case: hearing date, stage notes, links to uploaded artifacts as **string `s3_key`** (or FK to Person 4’s document version model **only if** their PR merged first; otherwise use `CharField`/`UUIDField` placeholders and a follow-up integration PR).
- **Plan of action (POA)** per hearing: deadline rule **≥ 2 calendar days before hearing** (Asia/Kolkata); compliance status (`PENDING`, `SUBMITTED`, `OVERDUE`), `submitted_at`, `s3_key` for upload metadata.
- Optional: opposite advocate details, legal opinion records (metadata + `s3_key`).

### 3.2 API

- DRF `ModelViewSet`s (or split read/write as needed) under `/api/v1/...` with **envelope**-compatible serializers (project already uses custom renderer; match existing land/geography patterns).
- **RBAC:** EXTERNAL_ADVOCATE: only assigned cases; no access to unrelated land revenue/investor endpoints (those modules do not exist yet — **do not** expose extra land fields beyond a minimal `LandFileMiniSerializer`-style read). IN_HOUSE_ADVOCATE: supervise all cases (per PRD). FOUNDER/MANAGEMENT: full. Other roles: explicit deny or read-only per PRD matrix — **document** your matrix in the app’s `README` or docstrings.
- Register ViewSets in **[`backend/apps/legal/urls.py`](../../backend/apps/legal/urls.py)** via `DefaultRouter` (that module is **already** included from [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py)).

### 3.3 Tests

- `pytest` tests colocated under `apps/legal/tests/` (or project convention).
- Cover: create case, create hearing, POA deadline logic (unit tests with frozen time if needed), RBAC matrix for **at least** FOUNDER, IN_HOUSE_ADVOCATE, EXTERNAL_ADVOCATE, and one denied role.

### 3.4 Celery (optional in your PR)

- If POA escalation is implemented now, use **`@shared_task(bind=True, max_retries=3)`** and **never** send WhatsApp/SMS synchronously in request cycle — stub or enqueue only. Full WhatsApp wiring may wait for Person 3’s notification service; coordinate via a **small integration PR** after both land.

---

## 4. Files and directories

### 4.1 You own (create/edit freely)

- `backend/apps/legal/**` (extend the existing app)
- New migration files under `apps/legal/migrations/` (`0002_…` onward)

### 4.2 You must NOT touch

- `backend/apps/revenue/**`, `backend/apps/tasks/**`, `backend/apps/documents/**` (other assignees)
- `frontend/**` (out of scope for this backend-only brief)
- **Do not** change existing land RBAC tests without coordination — extend with new tests in your app

### 4.3 Shared edits (only if necessary)

- `apps/users/permissions.py` — add new permission classes if cleaner than huge `get_permissions()` on ViewSets; keep changes minimal and documented in PR description.

---

## 5. Commands you must run before opening a PR

From repository root `/home/lucky/LIMP/limp` (adjust path if different):

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

**Before push, all of the following must pass:**

- `uv run ruff check .` (in `backend/`)
- `uv run ruff format --check .` (in `backend/`) — or run `ruff format` then recheck
- `uv run pytest` (in `backend/`)
- `pnpm check` (from root — includes frontend lint, typecheck, backend tests again, format check)

Optional but recommended (closest to full CI):

```bash
pnpm run ci
```

---

## 6. Git workflow (required)

1. `git checkout main && git pull --rebase origin main`
2. `git checkout -b feature/backend-person1-legal`
3. Commit logical chunks with clear messages.
4. `git push -u origin feature/backend-person1-legal`
5. Open a **Pull Request** to `main` on GitHub; describe RBAC, schema, and any follow-ups (S3 presign integration with Person 4).

**Never push directly to `main`** if your team uses PR review.

---

## 7. Merge / coordination notes

- **Land** is already the anchor; use FK `land` to `land.LandFile`.
- If Person 4’s document models are not merged yet, use **`s3_key` strings** on legal artifacts and switch to FK later in a thin migration.
- Kafka/Cassandra: do **not** put PII or full document payloads on Kafka ([`docs/rules.md`](../rules.md)).

---

*Brief version: April 2026 — Phase 1 foundation, production-grade patterns.*
