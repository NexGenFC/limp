# Backend — Architecture & Status

**Architecture map (models, FKs, related names):** [`ARCHITECTURE_BASE.md`](ARCHITECTURE_BASE.md)

---

## 🚀 Phase 1 Status: 75% Complete

We are currently transitioning from **Phase 1 Part 1 (Foundation)** to **Phase 1 Part 2 (Automation & Analytics)**.

| Person | Focus | Status | Current Brief |
|--------|-------|--------|---------------|
| **1** | Legal & Litigation | ⚠️ **In Progress (Part 1)** | [`ASSIGNMENT_01`](ASSIGNMENT_PERSON_01_LEGAL.md) |
| **2** | Revenue & Workflows | ✅ **COMPLETED (Part 1)** | [`ASSIGNMENT_02`](ASSIGNMENT_PERSON_02_REVENUE.md) |
| **3** | Tasks & Dashboard | ✅ **COMPLETED (Part 1)** | [`ASSIGNMENT_03`](ASSIGNMENT_PERSON_03_TASKS_NOTIFICATIONS.md) |
| **4** | Documents & S3 | ✅ **COMPLETED (Part 1)** | [`ASSIGNMENT_04`](ASSIGNMENT_PERSON_04_DOCUMENTS_STORAGE.md) |

---

## 🛠 Developer Setup

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

Full database guide: **[`docs/DEV_DATABASE.md`](../DEV_DATABASE.md)**.

---

## 🤝 Conflict Avoidance

*   **App Ownership**: Each person owns **one assigned Django app** under `backend/apps/<legal|revenue|tasks|documents>/`. Extend that app only.
*   **Standards**: All models **must** inherit from `BaseModel` (UUIDv7 + Audit + SoftDelete).
*   **RBAC**: ViewSets **must** override `get_queryset()` to enforce role scoping and `is_deleted=False`.
