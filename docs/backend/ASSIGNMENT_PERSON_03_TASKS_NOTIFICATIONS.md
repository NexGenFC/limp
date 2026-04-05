# Backend assignment — Person 3: Tasks, Notifications & Dashboard (Part 2)

**Owner:** Person 3 (Tasks / notifications / dashboard)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §12 (Tasks), §4.6 (Dashboard), HLD §3.4, §6 notification design.

**Core App:** `apps.tasks`  
**Integration Apps:** `apps.land` (Stats), `apps.legal` (Hearing counts), `apps.documents` (Completion %).

---

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Your app | `backend/apps/tasks/` | **Primary** — views, serializers, models, tests |
| URL Config | `backend/apps/tasks/urls.py` | Register the new dashboard router |
| Settings | `backend/config/settings/base.py` | Verify `apps.tasks` in `INSTALLED_APPS` |

### 0.2 Machine setup (New Session)

```bash
# From repo root
git checkout main && git pull --rebase origin main
cd backend && uv sync --all-groups && uv run python manage.py migrate
uv run python manage.py runserver 0.0.0.0:8000
```

---

## 1. Relevant Schema Reference

### 1.1 `apps.tasks.models.Task`
- `status`: Pending, In Progress, Completed, Overdue.
- `due_date`: Date field.
- `assigned_to`: FK to User.

### 1.2 `apps.tasks.models.NotificationLog`
- `status`: SENT, FAILED, PENDING.
- `message_summary`: string.
- `created_at`: datetime.

### 1.3 `apps.users.models.UserRole`
- Required for RBAC: `FOUNDER`, `MANAGEMENT`.

---

## 2. Your Scope — Current Status

### ✅ Phase 1 Part 1 — COMPLETED
- Task & Notification models foundation is live.
- Celery background workers for assignment & overdue checks are live.
- RBAC scoping on Task querysets is enforced.

### 🚀 Phase 1 Part 2 — Dashboard Aggregation (B10) — NEW
**Goal:** Implement the Founder's Command Center API.

#### 2.1 Requirements
- **Endpoint:** `GET /api/v1/dashboard/stats/`
- **RBAC:** Strictly restricted to `UserRole.FOUNDER` and `UserRole.MANAGEMENT`.
- **Payload Structure (JSON Example):**
  ```json
  {
    "land_stats": { "ACTIVE": 5, "NEGOTIATION": 2, "CLOSED": 10 },
    "task_stats": { "overdue_total": 3, "due_today": 1 },
    "legal_preview": { "hearings_next_7_days": 4 },
    "recent_activity": [
       { "id": "uuid", "message": "Task Assigned...", "status": "SENT", "timestamp": "ISO-DATE" }
    ],
    "document_stats": { "avg_completion_percentage": 0.85 }
  }
  ```

#### 2.2 Implementation Details
1. **Land Summary:** Aggregate `apps.land.models.LandFile` by the `status` field.
2. **Task Stats:** Filter `Task` where `status='OVERDUE'` and `due_date=today`.
3. **Legal Preview:** Count `apps.legal.models.LegalCase` with hearings scheduled in `now() + 7 days`.
4. **Recent Activity:** Return the latest 10 `NotificationLog` entries, ordered by `created_at` DESC.
5. **Document Health:** Call the service provided by Person 4: `apps.documents.services.get_overall_completion_stats()`.

---

## 3. Coordination & Conflicts

- **Coordination:** You MUST use Person 4's analytics service for the `document_stats` field. Do not re-implement the percentage logic in your app.
- **Conflict Avoidance:** 
  - Use `.aggregate()` and `.count()` only for `apps.land` and `apps.legal`.
  - **Do NOT** add `apps.legal` to your `models.py` imports; use `django.apps.apps.get_model` if necessary to avoid circular dependencies.

---

## 4. Verification

1. **Unit Test:** `apps/tasks/tests/test_dashboard.py`
   - Assert 200 OK for Founder.
   - Assert 403 Forbidden for `IN_HOUSE_ADVOCATE` or `FIELD_STAFF`.
   - Assert JSON keys match the structure in 2.1.
2. **Commands:**
   ```bash
   cd backend && uv run pytest apps/tasks/
   ```

---

*Brief version: April 2026 — Part 2 Update.*

