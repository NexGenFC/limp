# Backend assignment — Person 2: Revenue & government workflow module

**Owner:** Person 2 (Revenue / government workflows)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §5, PRD revenue workflow, [`docs/HLD.md`](../HLD.md) module map and ERD (revenue side).

**Base in repo:** `apps.revenue` with `GovernmentWorkflow`, `WorkflowKind` / `WorkflowStatus`, partial unique per `(land, kind)`. Extend via **new migrations**; APIs in `apps/revenue/urls.py`. [`ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md).

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Your app | `backend/apps/revenue/` | **Primary** |
| Land anchor | `backend/apps/land/` | FK target only (`land.LandFile`) |
| Geography | `backend/apps/geography/` | FKs for officer jurisdiction (reuse tables; do not duplicate) |
| Users | `backend/apps/users/` | RBAC patterns; optional FK to `User` for in-house revenue officer |

### 0.2 Documentation checklist (read before coding)

1. **This entire file.**
2. [`docs/rules.md`](../rules.md).
3. [`docs/PRD.md`](../PRD.md) — revenue / government workflow.
4. [`docs/HLD.md`](../HLD.md) — revenue module on land file.
5. [`docs/backend/ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md) — `government_workflows` on `LandFile`.
6. [`docs/COMPLETED.md`](../COMPLETED.md), [`docs/BACKLOG.md`](../BACKLOG.md), [`docs/IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md).
7. [`README.md`](../../README.md) — Path A, `pnpm check`.
8. [`docs/COCKROACHDB_MIGRATIONS.md`](../COCKROACHDB_MIGRATIONS.md) — **required** before adding indexes / constraints (you already have partial unique on `(land, kind)` in `0001`).
9. [`docs/DEV_DATABASE.md`](../DEV_DATABASE.md) — if `migrate` fails after pull.

### 0.3 Machine setup: first time and after every `git pull`

```bash
git checkout main && git pull --rebase origin main
cp .env.example .env   # once if needed

cd backend && uv sync --all-groups && uv run python manage.py migrate
cd backend && uv run python manage.py seed_demo_geography   # optional

cd backend && uv run python manage.py runserver 0.0.0.0:8000
```

**If `migrate` fails:** delete `backend/db.sqlite3` and re-run `migrate` — **[`docs/DEV_DATABASE.md`](../DEV_DATABASE.md)** explains why (schema / migration graph drift).

Before PR: from repo root — `pnpm install && pnpm check` (optional `pnpm run ci`).

### 0.4 Integration map (Revenue ↔ rest of LIMP)

| Connection | Detail |
|------------|--------|
| **Land** | FK **`land`** → `land.LandFile`. Reverse: `land.government_workflows`. |
| **Geography** | Link officers to `District` / `Taluk` / … as needed; read [`backend/apps/geography/models.py`](../../backend/apps/geography/models.py). |
| **Legal / tasks / documents** | **No dependency** for your first PR; do not edit those apps. |
| **URLs** | [`apps/revenue/urls.py`](../../backend/apps/revenue/urls.py) + `DefaultRouter`; wired via [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py). |

### 0.5 Code patterns to mirror

Same as Person 1 brief §0.5: [`apps/land/views.py`](../../backend/apps/land/views.py), [`apps/land/serializers.py`](../../backend/apps/land/serializers.py), [`apps/users/permissions.py`](../../backend/apps/users/permissions.py).

### 0.6 Local verification

- http://localhost:8000/api/v1/health/
- http://localhost:8000/api/schema/swagger/

---

## 1. Mandatory reading (before you write code)

1. [`docs/rules.md`](../rules.md) — soft delete, RBAC, envelope, `AuditedModel` / `SoftDeleteModel`, FK naming `land` for `LandFile`.
2. [`docs/HLD.md`](../HLD.md) — how revenue workflows hang off the land master file.
3. [`backend/apps/land/models.py`](../../backend/apps/land/models.py) — `LandFile` primary key and status patterns.
4. [`backend/apps/users/models.py`](../../backend/apps/users/models.py) — `UserRole`; [`permissions.py`](../../backend/apps/users/permissions.py) — extend consistently for revenue endpoints.

---

## 2. Toolchain you must use

| Tool | Requirement |
|------|----------------|
| **Python** | **3.12+** |
| **uv** | `cd backend && uv sync --all-groups`; run everything with **`uv run`** |
| **Node / pnpm** | **Node 22+**, **pnpm 10** (`pnpm@10.33.0` in root `package.json`) |
| **Git** | Feature branch + PR |

---

## 3. Your scope (what to build)

Work in the **existing** app **`apps.revenue`**.

### 3.1 Reference data (officers)

Model **government / revenue officers** relevant to the client brief (DC, AC, Tahsildar, Deputy Tahsildar, VA, RI, ADLR/DDLR, etc.):

- Prefer **normalization**: officer as an entity (name, designation enum, jurisdiction FKs to geography where applicable) rather than free text only.
- Optional link to **internal** revenue officer user (`FK` to `users.User`, nullable) for “in-house revenue officer” mapping.

### 3.2 Workflow instances per land

For each `land`, track multiple workflow rows for types such as:

- Mutation, Phodi, Tippani, RTC correction, Conversion (use enums; extensible via future migrations).

Each workflow row should support:

- Current status (enum), date applied, **officer handling** (FK), **days pending** (computed in serializer or DB-generated field — document), remarks, audit fields.

### 3.3 API & RBAC

- Authenticated API under `/api/v1/...` with DRF ViewSets, explicit `get_queryset()` filtering `is_deleted=False`.
- **FOUNDER** / **MANAGEMENT**: full CRUD as per PRD for this module.
- **REVENUE_TEAM**: read/write as per PRD (if PRD says full operational access, implement; otherwise read-only — **quote PRD section in PR description**).
- **EXTERNAL_ADVOCATE**, **SURVEYOR_FREELANCE**, **FIELD_STAFF**: **no access** to this module (403).
- Other roles: align with PRD §3.2; default to deny if unclear and note in PR.

Register ViewSets in **`apps/revenue/urls.py`** (`DefaultRouter`); it is already wired from [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py).

### 3.4 Tests

- CRUD happy paths for authorized roles.
- At least one test proving **EXTERNAL_ADVOCATE** (or FIELD_STAFF) receives **403** on create/list.
- Test **days pending** calculation with fixed dates if implemented as property.

---

## 4. Files and directories

### 4.1 You own

- `backend/apps/revenue/**` — entire package (already registered in settings and `api_v1_urls`)
- New migrations `0002_…` onward as needed

### 4.2 You must NOT touch

- `backend/apps/legal/**`, `backend/apps/tasks/**`, `backend/apps/documents/**`
- `frontend/**`

### 4.3 Geography linkage

- Reuse existing `District` / `Taluk` / `Hobli` / `Village` FKs where officer jurisdiction requires it; do **not** duplicate geography tables.

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

**All must pass before push.** Optional: `pnpm run ci` for production build parity.

---

## 6. Git workflow (required)

1. `git checkout main && git pull --rebase origin main`
2. `git checkout -b feature/backend-person2-revenue`
3. Push and open **PR to `main`**.

---

## 7. Merge / coordination notes

- No dependency on Person 1 or 4 for a minimal merge; only `LandFile` FK.
- Read [`docs/COCKROACHDB_MIGRATIONS.md`](../COCKROACHDB_MIGRATIONS.md) before adding unusual indexes or constraints.

---

*Brief version: April 2026 — Phase 1 foundation.*
