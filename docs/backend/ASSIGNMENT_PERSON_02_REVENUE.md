# Backend assignment — Person 2: Revenue & Automation (Part 2)

**Owner:** Person 2 (Revenue / government workflows)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §5, PRD revenue workflow, HLD §2 (Revenue Module).

**Core App:** `apps.revenue`  
**Integration Apps:** `apps.tasks` (Automation), `apps.land` (Anchor), `apps.geography` (Jurisdiction).

---

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Your app | `backend/apps/revenue/` | **Primary** — services, signals, analytics |
| Integration | `backend/apps/tasks/` | Consumer only (create tasks via service) |
| Geography | `backend/apps/geography/` | FK reference only |

### 0.2 Machine setup (New Session)

```bash
# From repo root
git checkout main && git pull --rebase origin main
cd backend && uv sync --all-groups && uv run python manage.py migrate
uv run pytest apps/revenue/tests/test_revenue_rbac.py  # Verify Part 1 foundation
```

---

## 1. Relevant Schema Reference

### 1.1 `apps.revenue.models.Officer`
- Already implemented with `BaseModel` (UUIDv7).
- Linked to `District`, `Taluk`, and `User` (internal_user).

### 1.2 `apps.revenue.models.GovernmentWorkflow`
- Tracked per `land` and `kind` (Mutation, Phodi, etc.).
- Includes `status` (APPLIED, IN_PROGRESS, COMPLETED).
- Includes `days_pending` computed property.

---

## 2. Your Scope — Current Status

### ✅ Phase 1 Part 1 — COMPLETED & SYNCED
- Officer and GovernmentWorkflow models are 100% standard-compliant.
- ViewSets with mandatory audit/soft-delete overrides are live.
- RBAC for `REVENUE_TEAM` is enforced.
- Migration history is consolidated into a clean initial state.

### 🚀 Phase 1 Part 2 — Revenue Automation (B17) — NEW
**Goal:** Automate internal follow-ups and provide hooks for the Founder Dashboard.

#### 2.1 Requirements — Task Automation
- **Logic:** When a `GovernmentWorkflow` status changes to `IN_PROGRESS` or `COMPLETED`, automatically create a `Task` in the `apps.tasks` module.
- **Payload Structure (Tasks):**
  - `title`: e.g., "Mutation Follow-up: [Land ID]"
  - `task_type`: `REVENUE_FOLLOWUP`
  - `assigned_to`: `officer_handling.internal_user` (if exists) or the `created_by` user.
  - `due_date`: `applied_on + 30 days`.
- **Implementation:** Implement a service `sync_workflow_tasks(workflow_id)` in `apps/revenue/services.py`. Call this from the ViewSet's `perform_update`. **Service Layer is mandatory.**

#### 2.2 Requirements — Analytics Hook (B10)
- **Logic:** Provide a clean data hook for the Dashboard (Person 3).
- **Service:** Implement `get_revenue_kpi_stats()` in `apps/revenue/services.py`.
- **Returned Data:**
  ```python
  {
      "pending_total": int, 
      "avg_days_pending": float, 
      "by_kind": {"PHODI": 2, "MUTATION": 5}
  }
  ```

---

## 3. Coordination & Conflicts

- **Coordination:** Person 3 (Dashboard) will call your `get_revenue_kpi_stats()` function. Ensure the function signature is stable.
- **Conflict Avoidance:** 
  - **Do NOT** import `apps.tasks.models.Task` directly in your `models.py` (prevents circular imports). 
  - **Do NOT** modify `apps.tasks` logic. Only create task records using their standard serializer or model via `django.apps.apps.get_model`.
  - **Consistency:** Maintain `BaseModel` usage and `PROTECT` on all new FKs.

---

## 4. Verification

1. **Unit Test:** `apps/revenue/tests/test_automation.py`
   - Assert `sync_workflow_tasks` correctly creates a `Task` in DB when triggered.
   - Assert `get_revenue_kpi_stats()` returns accurate counts for Dashboard.
2. **Commands:**
   ```bash
   cd backend && uv run pytest apps/revenue/tests/test_automation.py
   ```

---

*Brief version: April 2026 — Part 2 Update.*
