# Local development database — when to reset

**Audience:** Everyone working on `backend/` (Path A: SQLite, or Docker Cockroach).

---

## Path A — SQLite (`backend/db.sqlite3`)

### After `git pull`, usually

```bash
cd backend && uv sync --all-groups && uv run python manage.py migrate
```

If Django applies new migrations **without errors**, you **do not** need to delete the database.

### When you **must** delete `db.sqlite3` (and why)

Remove the file and run `migrate` again **when any** of these is true:

| Situation | Why |
|-----------|-----|
| **`migrate` fails** with errors about missing columns, unknown tables, or incompatible schema | Your SQLite file was built from an **older migration history** than `main`. Django cannot always “repair” a dev DB when we squash or replace initial migrations (e.g. switching land/domain tables to **UUIDv7** primary keys). |
| **Release notes / PR** say “reset local SQLite” | The team intentionally changed the migration graph; keeping the old file would leave you out of sync. |
| You want a **clean slate** (weird data, half-applied experiments) | Fastest fix is a fresh DB + `createsuperuser` + optional `seed_demo_geography`. |

**This is normal for early-phase projects.** It is **not** a production operation — production uses managed migrations and backups, not deleting the primary database.

### Commands (SQLite reset)

From repo root:

```bash
rm -f backend/db.sqlite3
cd backend && uv sync --all-groups && uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_demo_geography   # optional — land form dropdowns
```

Then sign in again in the UI and recreate any test land rows you need.

---

## Path B — Docker / CockroachDB

If you use Compose with Cockroach and your schema is broken or you need to match a clean `main`:

1. Stop the stack: `docker compose down`
2. Remove the Cockroach volume (this **wipes** CRDB data):  
   `docker volume rm limp_crdata`  
   (Volume name may differ; use `docker volume ls | grep limp` or `docker compose down -v` to remove all project volumes — **destructive**.)
3. `docker compose up --build` and let migrations run on the API container again.

---

## See also

- Root [`README.md`](../README.md) — Path A / B setup
- [`docs/backend/README.md`](backend/README.md) — backend assignee onboarding
- [`docs/COCKROACHDB_MIGRATIONS.md`](COCKROACHDB_MIGRATIONS.md) — production DDL checks

---

*April 2026 — keep this file updated when migration workflow changes.*
