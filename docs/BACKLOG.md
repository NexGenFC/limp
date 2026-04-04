# LIMP — backlog & not done (team sync)

**Purpose:** Single place for **what is not done yet** or **only partially done**, with **roles** called out where it matters for access control and demos.

**Sources:** [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md), PRD Phase 1 checklist, HLD.

**Update rule:** Pull items into [`COMPLETED.md`](COMPLETED.md) when shipped; keep this file honest and ordered by priority.

---

## Recently completed (moved from backlog)

| ID | Item | When |
|----|------|------|
| B1 | API RBAC on land endpoints (permissions.py, full role matrix tests) | April 2026 |
| B2 | Login UI + AuthGuard + Zustand session | April 2026 |
| B3 | Land Master UI (list, create with geography cascade, detail) | April 2026 |
| B4 | RoleGuard component + /403 page | April 2026 |

---

## Priority — remaining for client demo

| ID | Item | Status | Roles / notes |
|----|------|--------|----------------|
| B5 | Full Karnataka geography **seed** (production-scale) | Not in repo | Demo chain: run `python manage.py seed_demo_geography` (see README) |
| B6 | Refresh token in httpOnly cookie (instead of JS-accessible store) | Not done | Security improvement before production; rotate + blacklist already works |

## Backend parallel work (assignments)

Four non-overlapping backend briefs (branch + PR, `pnpm check` before push): **[`docs/backend/README.md`](backend/README.md)**.

## Product / Phase 1 (backend)

| ID | Item | Status | Roles / notes |
|----|------|--------|----------------|
| B7 | Legal cases, hearings, POA engine, documents vault | **Models scaffolded**; APIs / compliance engine not done | [`docs/backend/ARCHITECTURE_BASE.md`](backend/ARCHITECTURE_BASE.md) |
| B8 | Tasks module + notifications (WhatsApp / SMS) | **Models scaffolded**; APIs / Celery / channels not done | Tasks app has `Task`, `NotificationLog` |
| B9 | S3 **pre-signed** upload/download | **Models scaffolded** (`DocumentVersion`); presign endpoints not done | Person 4 brief |
| B10 | Dashboard aggregation endpoints | Not implemented | **FOUNDER**, **MANAGEMENT** |
| B11 | JWT **case_ids** / **task_ids** scoping for external advocate & freelance surveyor | Partially spec'd (HLD) | **EXTERNAL_ADVOCATE**, **SURVEYOR_FREELANCE** |

## Product / Phase 1 (frontend)

| ID | Item | Status | Roles / notes |
|----|------|--------|----------------|
| B12 | Legal, documents, tasks, founder dashboard pages | Not started | Per UI_UX_SPEC |
| B13 | Travel Mode, activity feed, KPI cards | Not started | **FOUNDER**-heavy |

## Infrastructure & ops

| ID | Item | Status | Notes |
|----|------|--------|-------|
| B14 | **CI job** optional: `migrate` + pytest against Cockroach (or compose) | Not started | Catches CRDB-only DDL issues |
| B15 | Production systemd / hardening docs for self-hosted CRDB + Kafka + Cassandra | Partial (ARCHITECTURE) | SRE handoff |

## Suggested client showcase (ready now)

1. Two users: **FOUNDER** and **MANAGEMENT** (or any read-only role to demonstrate RBAC denial).
2. Flow: **login → home → land list → create land file** (geography cascade) **→ view detail**.
3. Show that denied roles (e.g. FIELD_STAFF) are redirected to 403 or see no nav links.
4. **Prerequisite:** seed at least a few Districts/Taluks/Hoblis/Villages so the cascade works.

---

*Last updated: April 2026*
