# LIMP — Land Intelligence Management Platform

Monorepo for Abhivruddhi Ventures: Django REST API (`backend/`) and Next.js UI (`frontend/`). Product and engineering specs live in [`docs/`](docs/).

**Team sync:** what is done → [`docs/COMPLETED.md`](docs/COMPLETED.md) · what is not → [`docs/BACKLOG.md`](docs/BACKLOG.md) · engineering detail → [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md).

## Continuing on another machine or a fresh chat

The repo is the source of truth: **commit and push** when work is done. After cloning anywhere:

1. Read [`docs/COMPLETED.md`](docs/COMPLETED.md) (shipped scope + roles) and [`docs/BACKLOG.md`](docs/BACKLOG.md) (what is next).
2. Follow **Path A** below for day-to-day dev (no Docker required).
3. Lockfiles are committed: **`pnpm-lock.yaml`** (root) and **`backend/uv.lock`** — use `pnpm install` and `uv sync` so every machine gets the same dependency graph.
4. Never commit **`.env`** (it is gitignored). Always start from **`.env.example`**.
5. **After every `git pull`:** apply new Django migrations so your DB matches `main`:

   ```bash
   cd backend && uv sync --all-groups && uv run python manage.py migrate
   ```

   If `migrate` **errors** (schema mismatch), your local SQLite was built from older migrations. **Delete it and re-run migrate** — see **[`docs/DEV_DATABASE.md`](docs/DEV_DATABASE.md)** for the full reason and exact commands.

   (Same `uv sync` + `migrate` flow is part of **Path A §2** below for first-time backend setup.)

## Prerequisites

- **Node 22+** and **pnpm 10** (see root `packageManager` in [`package.json`](package.json))
- **uv** for Python ([astral.sh/uv](https://github.com/astral-sh/uv))
- **Docker** + Docker Compose **v2.20+** (optional but recommended for **CockroachDB**, **Kafka**, **Cassandra**, Redis, API, Celery, **audit-consumer** — see [`docker-compose.yml`](docker-compose.yml))

---

## Complete flow (choose one path)

### A — Minimal local (no Docker): SQLite + fast iteration

Use this for frontend work, quick API checks, and CI-equivalent runs.

1. **Clone and env**

   ```bash
   git clone <repo-url> && cd limp
   cp .env.example .env
   ```

   Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` (or your API host). Leave `DATABASE_URL` unset to use **SQLite** and **LocMem** cache (see `config/settings`).

2. **Backend**

   ```bash
   cd backend
   uv sync --all-groups
   uv run python manage.py migrate
   uv run python manage.py createsuperuser   # email + password; set role in admin if needed
   uv run python manage.py runserver 0.0.0.0:8000
   ```

3. **Frontend** (new terminal, repo root)

   ```bash
   pnpm install
   pnpm dev
   ```

4. **Demo geography** (so Land create dropdowns have data)

   ```bash
   cd backend
   uv run python manage.py seed_demo_geography
   ```

5. **Verify**

   - UI: [http://localhost:3000](http://localhost:3000) — redirects to login if not signed in
   - Sign in with the superuser email/password from step 2
   - In [Django admin](http://localhost:8000/admin/) → **Users**, set **Role** to `FOUNDER` or `MANAGEMENT` for full land CRUD (or use `IN_HOUSE_ADVOCATE` / `REVENUE_TEAM` / `SURVEYOR_INHOUSE` for read-only land; `FIELD_STAFF` / others should get **403** on land routes)
   - **Land flow:** Land Files → New Land File → pick District → Taluk → Hobli → Village → save → open detail from list
   - API health: [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/)
   - OpenAPI: [http://localhost:8000/api/schema/swagger/](http://localhost:8000/api/schema/swagger/)

6. **Quality gates** (before pushing)

   ```bash
   pnpm check
   ```

   That runs lint (frontend + backend Ruff), TypeScript, pytest, and Ruff format check — same checks as the backend job plus the frontend lint/type parts of CI. For a full match including **production build**:

   ```bash
   pnpm run ci
   ```

**Note:** With `KAFKA_BOOTSTRAP_SERVERS` unset, audit rows are **not** published to Kafka (by design). That matches CI.

**CORS:** If the UI cannot reach the API, ensure `.env` (backend) includes `CORS_ALLOWED_ORIGINS=http://localhost:3000` and `CSRF_TRUSTED_ORIGINS=http://localhost:3000` (see `.env.example`).

**Local DB problems after pulling?** Read **[`docs/DEV_DATABASE.md`](docs/DEV_DATABASE.md)** — when to delete `backend/db.sqlite3`, why, and how to reset safely.

### B — Full stack (Docker): CockroachDB + Redis + Kafka + Cassandra

Use this to mirror production-like data platform and run the **audit-consumer** pipeline.

1. **Env**

   ```bash
   cp .env.example .env
   ```

   For the **api** / **celery** services, Compose injects `DATABASE_URL` pointing at `cockroach:26257`. For tools on the host talking to exposed ports, uncomment in `.env`:

   - `DATABASE_URL=postgresql://root@localhost:26257/defaultdb?sslmode=disable`
   - `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`
   - `CASSANDRA_HOSTS=localhost`

2. **Start stack**

   ```bash
   docker compose up --build
   ```

   Wait for **`cassandra-init`** to complete (requires Compose v2.20+ `service_completed_successfully`).

3. **Verify**

   - CockroachDB UI: [http://localhost:8080](http://localhost:8080)
   - API (via Compose proxy): as configured in `docker-compose.yml` (typically port **8000** on host if published)
   - After a mutating API call, audit events flow: **OLTP `AuditLog`** → Celery → **Kafka** → **audit-consumer** → **Cassandra**

4. **Optional:** run Django on host against Compose DB

   ```bash
   cd backend
   export DATABASE_URL=postgresql://root@localhost:26257/defaultdb?sslmode=disable
   uv run python manage.py migrate
   uv run python manage.py runserver 0.0.0.0:8000
   ```

See [`docs/COCKROACHDB_MIGRATIONS.md`](docs/COCKROACHDB_MIGRATIONS.md) for DDL review and re-validation commands.

### Roles (eight) — where to look

Product and API use the same enum: **FOUNDER**, **MANAGEMENT**, **IN_HOUSE_ADVOCATE**, **EXTERNAL_ADVOCATE**, **REVENUE_TEAM**, **SURVEYOR_INHOUSE**, **SURVEYOR_FREELANCE**, **FIELD_STAFF**. Definitions: [`docs/COMPLETED.md`](docs/COMPLETED.md) and PRD §3. Code: `backend/apps/users/models.py` (`UserRole`).

---

## Quick start (local) — short version

Same as **path A** above: `cp .env.example .env` → `cd backend && uv sync --all-groups && uv run python manage.py migrate && uv run python manage.py createsuperuser && uv run python manage.py runserver` → from root `pnpm install && pnpm dev`.

## Root scripts

| Script | Purpose |
|--------|---------|
| `pnpm dev` | Next.js dev server (**Turbopack**) |
| `pnpm build` / `pnpm start` | Production Next build / serve |
| `pnpm lint` / `pnpm typecheck` | Frontend ESLint / `tsc` |
| `pnpm format` / `pnpm format:check` | Prettier |
| `pnpm update:safe` | Range-respecting dependency updates |
| `pnpm lint:be` / `pnpm test:be` | Ruff / pytest in `backend/` |
| `pnpm check` | **One command:** lint all, typecheck, pytest, Ruff format check (run before push) |
| `pnpm run ci` | Same as `check`, then `pnpm build` (closest local match to full GitHub CI). Use `pnpm run ci` so pnpm does not treat `ci` as a built-in. |

Backend formatting: `pnpm format:be` (Ruff format).

## API conventions

- Base path: **`/api/v1/`**
- Envelope: **`{ "success": true, "data": ..., "meta": {} }`** or **`success: false`** + `error` object (see [`docs/rules.md`](docs/rules.md))
- OpenAPI schema: **`/api/schema/`** (Swagger UI: `/api/schema/swagger/`, Redoc: `/api/schema/redoc/` — restrict or disable in production)
- Auth: **JWT** — `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`, `GET /api/v1/auth/me/` (Bearer access token)

## Docker Compose

With Docker running:

```bash
docker compose up --build
```

Services: **CockroachDB** (SQL UI on port **8080**, SQL on **26257**), **Kafka** (**9092**), **Cassandra** (**9042**), **Redis**, **Keycloak** (OIDC, port **8180**, admin: `admin`/`admin`), **api** (Gunicorn), **celery-worker**, **celery-beat**, **audit-consumer** (Kafka → Cassandra). Set `DJANGO_SECRET_KEY` for real use. Requires Docker Compose v2.20+ for `service_completed_successfully` on `cassandra-init`.

**Keycloak (optional):** When `KEYCLOAK_SERVER_URL` is set, the API accepts both SimpleJWT (direct login) and Keycloak-issued JWTs. Users auto-provision on first Keycloak login. Realm roles (`limp_founder`, `limp_management`, etc.) map to `UserRole`. See `.env.example` for config.

## CI

GitHub Actions (`.github/workflows/ci.yml`): frontend `lint`, `typecheck`, `build`; backend `ruff`, `pytest`.

## Documentation

| Doc | Purpose |
|-----|---------|
| [`docs/PRD.md`](docs/PRD.md) | Product requirements |
| [`docs/HLD.md`](docs/HLD.md) | Flows, ERD, compliance |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Stack and system design |
| [`docs/UI_UX_SPEC.md`](docs/UI_UX_SPEC.md) | UI/UX specification |
| [`docs/rules.md`](docs/rules.md) | Non‑negotiable engineering rules |
| [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) | Detailed FE/BE/infra truth (file-level) |
| [`docs/COMPLETED.md`](docs/COMPLETED.md) | Shipped scope — team sync |
| [`docs/BACKLOG.md`](docs/BACKLOG.md) | Not done / partial — priorities & roles |
| [`docs/COCKROACHDB_MIGRATIONS.md`](docs/COCKROACHDB_MIGRATIONS.md) | CockroachDB DDL review & checklist |
| [`docs/backend/README.md`](docs/backend/README.md) | Backend parallel work briefs (four owners) |
| [`docs/backend/ARCHITECTURE_BASE.md`](docs/backend/ARCHITECTURE_BASE.md) | Land-anchored domain apps & related names |
| [`docs/DEV_DATABASE.md`](docs/DEV_DATABASE.md) | When / why to reset local SQLite or Docker DB |

## Push changes to GitHub

From the repo root (after `pnpm check` or `pnpm run ci` passes):

```bash
git status
git pull --rebase origin main   # if others may have pushed
git push origin main
```

Use a **feature branch** + PR if your team prefers:

```bash
git checkout -b feature/your-topic
git push -u origin feature/your-topic
```

---

*Last updated: April 2026 — onboarding, manual verify steps, demo geography seed, push notes.*
