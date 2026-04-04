# Backend — parallel work assignments

**Architecture map (models, FKs, related names):** [`ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md)

**After `git pull`:** from repo root:

```bash
cd backend && uv sync --all-groups && uv run python manage.py migrate
```

If **`migrate` fails** (missing column, table, constraint errors), your machine still has an **old SQLite file** from before the team changed migrations (for example **UUIDv7** on domain tables or new apps). **Do not fight the error** — reset the dev DB:

```bash
rm -f backend/db.sqlite3
cd backend && uv sync --all-groups && uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_demo_geography   # optional
```

**Why:** SQLite in Path A is disposable; migration history on `main` is the source of truth. Full explanation: **[`docs/DEV_DATABASE.md`](../DEV_DATABASE.md)**.

Also documented in root [`README.md`](../../README.md).

---

Four self-contained briefs (one primary owner each). Each file includes **§0 Start here** (full reading list, setup, integration map). Read your brief end-to-end before coding.

| Person | Focus | Document |
|--------|--------|----------|
| 1 | Legal & litigation (cases, hearings, POA compliance hooks) | [`ASSIGNMENT_PERSON_01_LEGAL.md`](ASSIGNMENT_PERSON_01_LEGAL.md) |
| 2 | Revenue & government workflows | [`ASSIGNMENT_PERSON_02_REVENUE.md`](ASSIGNMENT_PERSON_02_REVENUE.md) |
| 3 | Tasks, notification log, Celery stubs (WhatsApp/SMS later) | [`ASSIGNMENT_PERSON_03_TASKS_NOTIFICATIONS.md`](ASSIGNMENT_PERSON_03_TASKS_NOTIFICATIONS.md) |
| 4 | Document vault checklist, versions, S3 pre-signed API | [`ASSIGNMENT_PERSON_04_DOCUMENTS_STORAGE.md`](ASSIGNMENT_PERSON_04_DOCUMENTS_STORAGE.md) |

**Shared:** Domain apps are already in `INSTALLED_APPS` and included from [`backend/config/api_v1_urls.py`](../../backend/config/api_v1_urls.py). Add **ViewSets and router registrations** inside your app’s `urls.py` only (do not duplicate `include` for the same app).

**Conflict avoidance:** Each person owns **one assigned Django app** under `backend/apps/<legal|revenue|tasks|documents>/` (already scaffolded). Extend that app only; do not edit another assignee’s app folder. Touch existing apps only when the brief explicitly allows it (usually `users.permissions` for new permission classes).
