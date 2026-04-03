# LIMP — Implementation status (engineering)

**Purpose:** Single place for what is **actually implemented** in the repo today (not roadmap). Updated April 2026.

---

## Frontend (`frontend/`)

| Area | Status | Notes |
|------|--------|--------|
| Framework | Done | Next.js 16 (App Router), React 19, TypeScript **strict** |
| Dev server | Done | `pnpm dev` → `next dev --turbopack` |
| Styling | Done | Tailwind CSS v4, shadcn/ui (base-nova), `components/ui/button` |
| Fonts | Done | Inter, DM Sans, JetBrains Mono (see `app/layout.tsx`) |
| Global state | Done | Zustand — `lib/stores/auth-store.ts` (access token + user in memory) |
| Server state | Done | TanStack Query — `app/providers.tsx` |
| API client | Done | Axios — `lib/api/client.ts` → `NEXT_PUBLIC_API_URL` + `/api/v1`, `withCredentials: true`, Bearer injection, 401 clears session |
| Env validation | Done | `lib/env.ts` (zod) + `getApiBaseUrl()` |
| **Login UI** | **Done** | `/login` — email/password form, calls `/auth/login/` + `/auth/me/`, sets Zustand session, redirects to `/` |
| **AuthGuard** | **Done** | `components/auth-guard.tsx` — wraps pages; redirects to `/login` if no token, `/403` if role denied |
| **RoleGuard** | **Done** | `components/role-guard.tsx` — renders children only if user role is in the allowed set |
| **403 page** | **Done** | `/403` — clean forbidden screen with back-to-home link |
| Layout | Done | `AppShell` — sidebar with role-aware nav links + user info + sign out |
| **Land list** | **Done** | `/land` — table with Land ID, survey, geography, acres, status, created date; links to detail |
| **Land create** | **Done** | `/land/new` — form with geography cascade (district → taluk → hobli → village), survey/hissa, extent, classification |
| **Land detail** | **Done** | `/land/[id]` — read-only card with all fields, geography breadcrumb, status badge |
| API helpers | Done | `lib/api/auth.ts`, `lib/api/land.ts`, `lib/api/geography.ts` — typed Axios wrappers |
| Domain UI (legal, docs, tasks) | **Not done** | Not scaffolded |
| Production build | Done | `output: 'standalone'` in `next.config.ts` |

**Quality gates:** `pnpm lint`, `pnpm typecheck`, `pnpm build` (from repo root via workspace).

---

## Backend (`backend/`)

| Area | Status | Notes |
|------|--------|--------|
| Django | Done | 6.x, `config/settings/{base,development,production}.py` |
| Package mgmt | Done | `uv` + `pyproject.toml` + `uv.lock` |
| API envelope | Done | `EnvelopeJSONRenderer` + `custom_exception_handler` — `{ success, data\|error, meta }` |
| OpenAPI | Done | `drf-spectacular` — `/api/schema/`, Swagger, Redoc |
| Auth | Done | SimpleJWT — `POST /api/v1/auth/login/`, `refresh/`, `logout/`, `me/`; custom user **email** login; roles in JWT claims |
| Rate limit | Done | `django-ratelimit` on login; DRF throttles globally |
| Custom user | Done | `apps.users` — `UserRole` enum (8 roles per HLD), `UserManager` |
| Core mixins | Done | `apps.core.models` — `TimeStampedModel`, `AuditedModel`, `SoftDeleteModel`, `BaseModel`, `ActiveManager` |
| **RBAC permissions** | **Done** | `apps.users.permissions` — `LandPermission`, `IsFounder`, `IsFounderOrManagement`; applied to `LandFileViewSet` |
| Geography | Done | `District` → `Taluk` → `Hobli` → `Village` (read-only ViewSets; filter query params; `IsAuthenticated`); **`manage.py seed_demo_geography`** for local demo data |
| Land Master | Done | `LandFile` on `BaseModel`; auto `LIMP-YYYY-NNNN`; CRUD; `DELETE` → **soft delete**; `LandPermission` enforced |
| Audit (OLTP) | Done | `AuditLog` model; `AuditMiddleware` on mutating `/api/` requests; append-only in admin |
| Telemetry / Kafka | Done | `apps.telemetry.tasks.publish_audit_log_event` — publishes to Kafka when `KAFKA_BOOTSTRAP_SERVERS` set |
| Cassandra consumer | Done | `scripts/audit_kafka_consumer.py` — Kafka → `limp.audit_logs` |
| Celery | Done | `config/celery.py`; heartbeat beat schedule; eager mode default in **development** settings |
| Tests | Done | `pytest` — 25 tests: health, login, land CRUD + **full RBAC matrix** (all 8 roles) |
| RBAC on domain APIs | **Done (land)** | Land: Full CRUD for FOUNDER/MANAGEMENT; read-only for IH Advocate/Revenue/Surveyor IH; denied for Ext Advocate/FL Surveyor/Field Staff |
| Legal / documents / tasks | **Not done** | Not scaffolded |
| S3 presigned uploads | **Not done** | Not implemented |
| WhatsApp / SMS | **Not done** | Not implemented |

**Quality gates:** `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`.

---

## Containerisation (`docker-compose.yml`)

| Service | Role |
|---------|------|
| `cockroach` | Primary OLTP (PostgreSQL protocol), port `26257`, UI `8080` |
| `redis` | Celery + cache |
| `cassandra` + `cassandra-init` | Keyspace/table for audit copies |
| `kafka` | KRaft single broker, port `9092` |
| `api` | Gunicorn + migrations |
| `celery-worker` / `celery-beat` | Background work |
| `audit-consumer` | `scripts/audit_kafka_consumer.py` |

**Local without Docker:** SQLite + LocMem cache + eager Celery; Kafka publish **no-op** if env unset.

---

## Documentation set

| File | Role |
|------|------|
| `docs/PRD.md` | Product requirements (updated for data platform NFRs) |
| `docs/HLD.md` | Flows + ERD + audit pipeline note |
| `docs/ARCHITECTURE.md` | Stack + Cockroach/Kafka/Cassandra section |
| `docs/UI_UX_SPEC.md` | UI spec (stack line aligned) |
| `docs/rules.md` | Agent + team rules (data platform rules added) |
| `docs/IMPLEMENTATION_STATUS.md` | **This file** — implementation truth |
| `docs/COMPLETED.md` | Shipped scope summary (roles + modules) for team sync |
| `docs/BACKLOG.md` | Not done / partial — IDs, priorities, role notes |
| `docs/COCKROACHDB_MIGRATIONS.md` | Django migrations reviewed for CockroachDB compatibility |

---

## Recommended next (client showcase)

1. **Geography seed data** (Karnataka hierarchy) so the create-land cascade is populated.
2. **Harden** refresh token strategy (httpOnly cookie for refresh, not just in-memory access token).
3. Legal, documents, tasks modules (backend + frontend).

Do **not** showcase without verifying RBAC in the browser — tested at API level (25 tests), but manual smoke test with two different-role users is recommended.
