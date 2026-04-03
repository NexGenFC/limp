# LIMP — completed work (team sync)

**Purpose:** Human-readable list of **what is already shipped** in the repo so product, design, and engineering stay aligned. For raw detail per file, see [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

**Update rule:** When a backlog item ships, move its description here (or summarize) and trim [`BACKLOG.md`](BACKLOG.md).

---

## Roles in scope (product ↔ code)

These eight roles are defined in code (`UserRole` in `backend/apps/users/models.py`) and in the PRD/HLD. **Implemented:** model + JWT claims on login + **API RBAC on land endpoints** + **frontend RoleGuard + AuthGuard**.

| Role code | Label (short) | Land Master access |
|-----------|-----------------|---------------------|
| `FOUNDER` | Founder / Super Admin | Full CRUD |
| `MANAGEMENT` | Management | Full CRUD |
| `IN_HOUSE_ADVOCATE` | In-House Advocate | Read-only |
| `EXTERNAL_ADVOCATE` | External Advocate | Denied (needs case scoping) |
| `REVENUE_TEAM` | Revenue Team | Read-only |
| `SURVEYOR_INHOUSE` | Surveyor (In-House) | Read-only |
| `SURVEYOR_FREELANCE` | Surveyor (Freelance) | Denied |
| `FIELD_STAFF` | Field Staff | Denied |

---

## Repository & tooling

- Monorepo: **pnpm** workspace (frontend) + **uv** (backend), root scripts for lint/typecheck/tests.
- **GitHub Actions** CI: frontend lint, typecheck, build; backend ruff + pytest (SQLite, no Kafka).
- **Docker Compose**: CockroachDB, Redis, Kafka (KRaft), Cassandra + init, API, Celery worker/beat, audit-consumer.

---

## Backend (Django / DRF)

- Settings split: `development` / `production`; `DATABASE_URL` (PostgreSQL/Cockroach) or SQLite fallback.
- **Envelope** JSON responses and **drf-spectacular** OpenAPI.
- **JWT** (SimpleJWT): login (email), refresh, logout, me — with **role in token payload**.
- **Rate limiting** on login + DRF throttling.
- **Core mixins:** timestamps, audit user fields, soft delete, `ActiveManager`.
- **Geography API:** District → Taluk → Hobli → Village (read-only ViewSets, filters).
- **Land Master API:** `LandFile` CRUD, generated `land_id`, soft delete on DELETE.
- **RBAC permissions:** `LandPermission` in `apps/users/permissions.py` — enforces PRD §3.2 access matrix on land endpoints. **25 tests** cover all 8 roles + unauthenticated.
- **Audit (OLTP):** `AuditLog` + middleware on mutating `/api/` calls.
- **Telemetry:** Celery task publishes audit events to Kafka when configured; **no-op** if `KAFKA_BOOTSTRAP_SERVERS` unset.
- **Consumer script:** Kafka → Cassandra (`scripts/audit_kafka_consumer.py`).
- **CockroachDB migrations:** reviewed — [`COCKROACHDB_MIGRATIONS.md`](COCKROACHDB_MIGRATIONS.md).

---

## Frontend (Next.js)

- App Router, TypeScript strict, Tailwind v4, shadcn/ui base, TanStack Query, Zustand auth store (access token + user in memory), Axios client with Bearer + 401 handling.
- **Login page** (`/login`): email/password form → JWT tokens → fetch `/auth/me/` → Zustand session.
- **AuthGuard** component: wraps protected pages; redirects to `/login` if no token, `/403` if role mismatch.
- **RoleGuard** component: conditionally renders UI elements based on user role.
- **403 page**: clean forbidden screen.
- **App shell** (sidebar layout): role-aware nav, user info, sign-out button.
- **Land list** (`/land`): table with geography, status badges, links to detail — only for roles with read access.
- **Land create** (`/land/new`): form with **geography cascade** (district → taluk → hobli → village), survey/hissa, extent, classification — only for FOUNDER/MANAGEMENT.
- **Land detail** (`/land/[id]`): read-only card with all fields.
- **API helpers**: typed wrappers in `lib/api/auth.ts`, `lib/api/land.ts`, `lib/api/geography.ts`.
- **Production:** `standalone` output for container deploys.

---

## Documentation

- PRD, HLD, ARCHITECTURE, UI_UX_SPEC, rules — product/architecture baseline.
- **IMPLEMENTATION_STATUS** — engineering truth table.
- **COCKROACHDB_MIGRATIONS** — DDL review for CRDB.
- **COMPLETED** (this file) / **BACKLOG** — team sync.

---

*Last updated: April 2026*
