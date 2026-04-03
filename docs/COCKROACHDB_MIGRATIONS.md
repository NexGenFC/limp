# CockroachDB — migration review (Django ↔ CRDB)

**Purpose:** Record how LIMP’s Django migrations relate to **CockroachDB** (PostgreSQL wire protocol) so the team does not ship DDL that works on SQLite or vanilla Postgres but fails on CRDB.

**Last reviewed:** April 2026 (initial LIMP apps).

---

## Summary

All **LIMP-owned** initial migrations were reviewed at the **Django migration operation** level (fields, constraints, indexes). They use standard patterns that CockroachDB supports in PostgreSQL-compatibility mode:

| App | Migration | Notes |
|-----|-----------|--------|
| `users` | `0001_initial` | `BigAutoField`, `EmailField`, `CharField` choices, M2M to `auth` — compatible. Depends on `auth.0012_*` (Django core). |
| `geography` | `0001_initial` | `BigAutoField`, `ForeignKey` + `PROTECT`, `unique_together` → `UNIQUE` constraints — compatible. |
| `land` | `0001_initial` | `DecimalField`, multiple `ForeignKey` to `User` (`SET_NULL` / `PROTECT`), `JSON`-free — compatible. |
| `audit` | `0001_initial` | `JSONField` (PostgreSQL backend → **JSONB**), `GenericIPAddressField`, composite `models.Index` — compatible with CRDB JSONB / indexing rules. |

**Verdict:** No migration edits were required for the current codebase. **Future** migrations must be checked before merge (see checklist below).

---

## How to re-validate SQL (when Cockroach is running)

From `backend/`:

```bash
export DATABASE_URL='postgresql://root@localhost:26257/defaultdb?sslmode=disable'
uv run python manage.py sqlmigrate geography 0001
uv run python manage.py sqlmigrate land 0001
uv run python manage.py sqlmigrate audit 0001
uv run python manage.py sqlmigrate users 0001
```

Compare output with [CockroachDB known limitations](https://www.cockroachlabs.com/docs/stable/postgresql-compatibility) for your server version.

---

## CockroachDB vs PostgreSQL — what to watch in new migrations

1. **`SERIAL` / implicit sequences** — Django’s `AutoField` / `BigAutoField` map to identity-like columns; CRDB supports this in PG mode. Avoid hand-written `RunSQL` that assumes **session-level** `nextval()` semantics that differ across engines.
2. **`CREATE INDEX CONCURRENTLY` / `AddIndexConcurrently`** — Django can emit concurrent index builds on PostgreSQL. CockroachDB uses **online schema** differently; if a migration sets `atomic = False` and uses concurrent operations, **test on CRDB** before merging.
3. **Postgres-only types** — Avoid raw SQL using `CITEXT`, `LTREE`, `HSTORE`, custom enums not declared in CRDB, etc., unless documented and tested.
4. **`EXCLUDE` constraints / GiST / GIN** — Not used in LIMP migrations today; if added, verify CRDB support for your version.
5. **`RunPython` + raw SQL** — Treat as high risk; prefer ORM operations or reviewed `RunSQL` with CRDB CI/staging.
6. **Django `contrib` migrations** — Full `migrate` on an empty database runs `auth`, `admin`, `sessions`, etc. Run **`migrate` against a throwaway CRDB instance** when upgrading Django major versions.

---

## JSON / audit

- `AuditLog.old_value` / `new_value` use Django **`JSONField`**. On the PostgreSQL backend this is **JSONB** — aligned with [`docs/rules.md`](rules.md) database rules and supported on CockroachDB.

---

## Related docs

- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — §2.1 data platform, §7 database architecture  
- [`docs/rules.md`](rules.md) — DATA PLATFORM RULES  
- [`README.md`](../README.md) — Docker Compose and `DATABASE_URL`
