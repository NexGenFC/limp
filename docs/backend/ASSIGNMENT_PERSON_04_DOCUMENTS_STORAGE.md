# Backend assignment — Person 4: Document vault & S3 pre-signed API

**Owner:** Person 4 (Documents / storage)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §7, HLD §3.3 document upload flow, BACKLOG B9, [`docs/rules.md`](../rules.md) §NO FILES ON DISK.

**Base in repo:** `apps.documents` with `LandDocumentChecklistItem`, `DocumentKind` / `ChecklistStatus`, and `DocumentVersion` (`s3_key`, metadata). Add boto3 + presign views; extend via **new migrations**. [`ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md).

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Your app | `backend/apps/documents/` | **Primary** — presign views, serializers, `urls.py`, tests |
| Land | `backend/apps/land/` | RBAC must align with who can see which `land_id` |
| Dependencies | `backend/pyproject.toml`, `backend/uv.lock` | Add **boto3** (and **moto** dev if you use it) via `uv add` |
| Env | [`.env.example`](../../.env.example) (repo root) | Document S3 variable **names** only |

### 0.2 Documentation checklist (read before coding)

1. **This entire file.**
2. [`docs/rules.md`](../rules.md) — **no** file bodies on Django disk; `s3_key` only; encryption/sensitive data rules for future KYC module.
3. [`docs/PRD.md`](../PRD.md) — document vault / checklist.
4. [`docs/HLD.md`](../HLD.md) — §3.3 upload flow.
5. [`docs/backend/ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md) — checklist + versions; `document_checklist_items` on `LandFile`.
6. [`docs/COMPLETED.md`](../COMPLETED.md), [`docs/BACKLOG.md`](../BACKLOG.md), [`docs/IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md).
7. [`README.md`](../../README.md) — `pnpm check`.
8. [`docs/COCKROACHDB_MIGRATIONS.md`](../COCKROACHDB_MIGRATIONS.md) — partial unique on checklist `(land, document_kind)`.
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

Before PR: `pnpm install && pnpm check` (optional `pnpm run ci`). **CI must pass without real AWS** (moto or skip).

### 0.4 Integration map (Documents ↔ rest of LIMP)

| Connection | Detail |
|------------|--------|
| **Land** | Checklist FK **`land`**; reverse `land.document_checklist_items`. |
| **Legal** | After your API is stable, Person 1 may FK `DocumentVersion` for pleadings/orders — coordinate in a small follow-up PR. |
| **Users** | `uploaded_by` on `DocumentVersion`; enforce land-level RBAC on presign. |
| **URLs** | [`apps/documents/urls.py`](../../backend/apps/documents/urls.py); included from [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py). |

### 0.5 Code patterns to mirror

Land RBAC for “can this user touch this land?” — [`apps/users/permissions.py`](../../backend/apps/users/permissions.py), [`apps/land/views.py`](../../backend/apps/land/views.py).

### 0.6 Local verification

- http://localhost:8000/api/v1/health/
- http://localhost:8000/api/schema/swagger/

---

## 1. Mandatory reading (before you write code)

1. [`docs/rules.md`](../rules.md) — **no** storing uploads on Django local disk; store **`s3_key`** in DB; pre-signed upload/download; soft delete; envelope; audit.
2. [`docs/HLD.md`](../HLD.md) §3.3 — presign → PUT to S3 → confirm upload → version row.
3. [`backend/apps/core/models.py`](../../backend/apps/core/models.py) — `BaseModel` mixins.
4. [`backend/config/settings`](../../backend/config/settings/) — how env vars are loaded (`django-environ`); add **optional** S3 settings with safe defaults for CI (tests use mocks or skip if unset).

---

## 2. Toolchain you must use

| Tool | Requirement |
|------|----------------|
| **Python** | **3.12+** |
| **uv** | `cd backend && uv sync --all-groups`; use **`uv run`** |
| **Node / pnpm** | **Node 22+**, **pnpm 10** |
| **Git** | Feature branch + PR |

### Dependencies

- Add S3 client via **boto3** (or equivalent) through **`pyproject.toml`** with `uv add boto3` (or `uv add --dev` for test helpers); run **`uv lock`** and commit **`uv.lock`**.

---

## 3. Your scope (what to build)

Work in the **existing** app **`apps.documents`**.

### 3.1 Land document checklist

- **`LandDocumentChecklistItem`** exists with `document_kind`, `checklist_status`, `remarks`. Extend kinds/statuses or add reference tables via new migrations if product requires.

### 3.2 Versioning

- **`DocumentVersion`** exists (`s3_key`, `original_filename`, `content_type`, `size_bytes`, `uploaded_by`). Add presign/confirm flows and tighten RBAC in views — **no hard delete**.

### 3.3 Pre-signed API (HLD)

Expose endpoints from **`apps/documents/urls.py`** (already included via [`config/api_v1_urls.py`](../../backend/config/api_v1_urls.py)).

Endpoints (names illustrative — align with OpenAPI and existing URL style):

1. **Presigned upload** — POST: land id, doc type / checklist row id, filename, content type → returns `upload_url`, `s3_key`, expiry.
2. **Confirm upload** — POST: `s3_key`, checklist row id → creates new `DocumentVersion`, bumps version, updates status.
3. **Presigned download** — GET or POST: version id → short-lived download URL.

**Security:**

- RBAC: only roles allowed to see that **land** may request URLs (reuse patterns from land permissions; extend with new permission classes as needed).
- **Never** return bucket-wide or long-lived credentials to the client.

### 3.4 Environment / CI

- When AWS keys / bucket are **unset** (local CI), endpoints should return **400/503** with clear error **or** be test-only mocked — **pytest must pass without real AWS**.
- Document required env vars in **repo root [`.env.example`](../../.env.example)** (same pattern as the rest of the project).

### 3.5 Tests

- Use **moto** or mock boto3 client to test presign + confirm flow without network **or** gate integration tests with `pytest.mark.skipif`.
- RBAC: forbidden role cannot obtain presign for a land they cannot access.

---

## 4. Files and directories

### 4.1 You own

- `backend/apps/documents/**` (already registered in settings and `api_v1_urls`)
- New migrations `0002_…` onward as needed
- Updates to **`pyproject.toml` / `uv.lock`** for boto3 (and moto if used)
- `.env.example` entries for S3 bucket/region/credentials **names only** (no secrets)

### 4.2 You must NOT touch

- `backend/apps/legal/**`, `backend/apps/revenue/**`, `backend/apps/tasks/**`
- `frontend/**`

### 4.3 Coordination with Person 1

- Once your models exist, legal can FK to `DocumentVersion` in a **later** PR; your first PR should be mergeable with **only** `land` FKs.

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
2. `git checkout -b feature/backend-person4-documents-s3`
3. Open **PR to `main`**.

---

## 7. Merge / coordination notes

- S3 bucket layout: use a deterministic key prefix e.g. `land/{land_id}/{doc_type}/{uuid}_{filename}` — document in PR.
- CockroachDB: follow [`docs/COCKROACHDB_MIGRATIONS.md`](../COCKROACHDB_MIGRATIONS.md) for JSON/index choices.

---

*Brief version: April 2026 — Phase 1 foundation.*
