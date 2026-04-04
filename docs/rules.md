# LIMP — AI Agent Coding Rules
# Land Intelligence Management Platform
# For use in: Cursor, Kiro IDE, GitHub Copilot, or any AI coding assistant

---

## PROJECT IDENTITY

This is the **Land Intelligence Management Platform (LIMP)** — an enterprise-grade operational system for Abhivruddhi Ventures, a Karnataka-based real estate and land acquisition company.

**Stack:** Django 6.x + DRF · Next.js (React 19) + TypeScript strict · **CockroachDB** (primary OLTP, PostgreSQL wire protocol) · **Redis** · **Celery** · **Apache Kafka** (events) · **Apache Cassandra** (audit log fan-out) · optional **Keycloak** (OIDC) · private S3-compatible storage · uv (Python) · pnpm (Node)  
**Current Phase:** Phase 1 — Foundation  
**Repo layout:**
```
/backend/         → Django project (`config/`, `apps/*`, `manage.py`, `pyproject.toml`, `uv.lock`)
/frontend/        → Next.js App Router (Turbopack in dev), shadcn/ui + Tailwind
/docs/            → PRD, ARCHITECTURE, HLD, UI/UX spec, this file
```

---

## ABSOLUTE RULES — NEVER VIOLATE

### 1. NO HARD DELETES — EVER
```python
# ❌ NEVER do this
instance.delete()
MyModel.objects.filter(...).delete()

# ✅ ALWAYS soft delete
instance.soft_delete(user=request.user)
# or
instance.is_deleted = True
instance.deleted_at = timezone.now()
instance.deleted_by = request.user
instance.save()
```
This is a legal/compliance system. Hard deletes are a critical bug.

### 2. RBAC MUST BE ENFORCED AT THE API LAYER — NOT JUST FRONTEND
```python
# ❌ NEVER rely on frontend to hide data
# ❌ NEVER trust that "the UI won't show it"

# ✅ ALWAYS filter queryset based on user role
def get_queryset(self):
    user = self.request.user
    qs = LegalCase.objects.filter(is_deleted=False)
    if user.role == UserRole.EXTERNAL_ADVOCATE:
        qs = qs.filter(assigned_advocates=user)
    return qs

# ✅ ALWAYS check permissions before any action
permission_classes = [IsAuthenticated, IsInHouseAdvocateOrAbove]
```

### 3. EVERY MODEL MUST INHERIT FROM BASE MIXINS
```python
# ✅ All models must inherit from AuditedModel + SoftDeleteModel
class LegalCase(AuditedModel, SoftDeleteModel):
    ...

# These provide:
# created_at, updated_at, created_by, updated_by (AuditedModel)
# is_deleted, deleted_at, deleted_by (SoftDeleteModel)
```

### 4. NO FILES STORED ON DJANGO SERVER / EC2 DISK
```python
# ❌ NEVER save uploaded files to local filesystem
# ❌ NEVER use default_storage with FileSystemStorage for uploads

# ✅ All files go to S3 via pre-signed URLs
# ✅ Store only the s3_key (string) in the database
# ✅ Generate pre-signed download URLs on request (15 min expiry)
```

### 5. NO SENSITIVE DATA IN PLAIN TEXT
```python
# ❌ NEVER store these as plain CharField
aadhaar_number = models.CharField(...)  # WRONG

# ✅ Use EncryptedCharField for:
# - Aadhaar numbers
# - PAN numbers
# - Bank account numbers
# - Investor financial capacity data
from encrypted_fields.fields import EncryptedCharField
aadhaar_number = EncryptedCharField(max_length=12)
```

### 6. ALL API RESPONSES MUST USE THE STANDARD FORMAT
```python
# ✅ Success
return Response({
    "success": True,
    "data": serializer.data,
    "meta": {"page": 1, "total": 42}
})

# ✅ Error
return Response({
    "success": False,
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "You do not have access to this resource."
    }
}, status=status.HTTP_403_FORBIDDEN)

# ❌ Never return raw serializer.data without the wrapper
# ❌ Never return unstructured error strings
```

### 7. EVERY MUTATING ACTION MUST CREATE AN AUDIT LOG ENTRY
```python
# ✅ The AuditMiddleware handles this automatically for API requests
# ✅ But for Celery tasks and background jobs, log manually:
AuditLog.objects.create(
    user=user,
    action='UPDATE',
    model_name='Hearing',
    object_id=hearing.id,
    old_value={'poa_status': 'PENDING'},
    new_value={'poa_status': 'OVERDUE'},
    ip_address=None  # background job — no IP
)
```

---

## DJANGO RULES

### Models
- All models go in `apps/{module}/models.py`
- Always define `__str__`, `class Meta` with `ordering`, `verbose_name`, `verbose_name_plural`
- Always use `related_name` on FK fields — never rely on default `_set`
- Use `on_delete=models.PROTECT` for critical FKs (land_file, legal_case) — never CASCADE delete
- Use `on_delete=models.SET_NULL` for user references on non-critical fields
- All querysets must filter `is_deleted=False` by default — use a custom `ActiveManager`

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class LegalCase(AuditedModel, SoftDeleteModel):
    objects = ActiveManager()
    all_objects = models.Manager()  # use only for admin/audit purposes
```

### Views / ViewSets
- Always use `ModelViewSet` for standard CRUD
- Always override `get_queryset()` — never use model.objects directly in views
- Always override `get_permissions()` for action-specific permissions
- Always override `perform_create()` to inject `created_by=request.user`
- Use `@action` decorator for non-CRUD endpoints on a resource

```python
def perform_create(self, serializer):
    serializer.save(
        created_by=self.request.user,
        updated_by=self.request.user
    )

def perform_update(self, serializer):
    serializer.save(updated_by=self.request.user)
```

### Serializers
- Always use `ModelSerializer`
- Always declare `fields` explicitly — never use `fields = '__all__'`
- Read-only fields: `created_at`, `updated_at`, `created_by`, `updated_by`, `land_id`
- Nested serializers for read: use `LandFileMiniSerializer` (id + land_id + village name only)
- Write operations: accept FK id, not nested object

### URLs
- All URLs under `/api/v1/`
- Use DRF `DefaultRouter` for ViewSets
- URL naming: `land-list`, `land-detail`, `legal-case-list`, etc.

### Settings
- Never hardcode secrets — always use `os.environ.get()`
- Use `config/settings/base.py`, `development.py`, `production.py`
- `DEBUG=True` only in development — never in production
- `ALLOWED_HOSTS` must be set in production settings

### Migrations
- Always run `makemigrations` after model changes
- Never edit existing migration files — create new ones
- Migration files must be committed to the repository

---

## CELERY RULES

- All task functions must be decorated with `@shared_task`
- All task functions must have `bind=True` and `max_retries=3`
- Always use `.delay()` or `.apply_async()` — never call task functions directly
- Task functions must be idempotent — safe to run multiple times

```python
@shared_task(bind=True, max_retries=3)
def send_task_assignment_notification(self, task_id):
    try:
        task = Task.objects.get(id=task_id)
        NotificationService().send(task.assigned_to_id, ...)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * 15)  # retry in 15 min
```

---

## REACT RULES

### General
- Functional components only — no class components
- **TypeScript strict** is required for the Next.js app
- All API calls go through `frontend/lib/api/` (shared axios client) — never use `fetch`/raw axios directly in feature components
- No hardcoded API URLs in components — use `NEXT_PUBLIC_API_URL` and `getApiBaseUrl()` / `apiClient`

### State Management
- Use Zustand for global state (auth, current user, notifications)
- Use React Query (`@tanstack/react-query`) for server state (API data, caching)
- Do NOT use useEffect + useState for API calls — use React Query hooks

### Authentication
- Store access token in memory (Zustand store)
- Store refresh token in httpOnly cookie
- Never store tokens in localStorage
- Use Axios request interceptor to inject Authorization header

### Role-Based Rendering
- Wrap all sensitive UI in `<RoleGuard roles={[...]}>`
- Never use inline role checks like `{user.role === 'FOUNDER' && <Button />}` — always use RoleGuard
- If a user navigates to a restricted route, redirect to `/403` — never just hide the nav link

### Forms
- Use React Hook Form for all forms
- All form submissions show loading state on the submit button
- All form errors displayed inline next to the relevant field
- Never disable the back button or navigation while a form is submitting

### File Uploads
- Always use the pre-signed S3 upload flow — never POST files to the Django backend
- Show upload progress bar for files > 1MB
- Validate file size and type on the client before requesting pre-signed URL

---

## DATA PLATFORM RULES (CockroachDB · Kafka · Cassandra)

- **Primary OLTP** is **CockroachDB** in production Compose/self-hosted deployments; **SQLite** is acceptable for CI and local tests without Docker. **Concrete review** of LIMP migrations and a checklist for new DDL: **[`docs/COCKROACHDB_MIGRATIONS.md`](COCKROACHDB_MIGRATIONS.md)** — read it before merging schema-heavy PRs.
- **Kafka payloads** must stay **minimal** and **non-sensitive by default** (IDs, model name, action, structured diff). Do **not** place Aadhaar, PAN, bank details, or full document content on Kafka without explicit security review and encryption strategy.
- **Cassandra** holds **append-style audit copies** from Kafka; it does **not** replace RBAC or the transactional `audit_log` table in the primary database for authorization decisions.
- If Kafka or Cassandra is unavailable, **API correctness must not break**: publishing uses Celery with retries; failures are logged — the primary `AuditLog` row still commits first.

## DATABASE RULES

- All new tables need a `created_at` and `updated_at` column minimum
- Every FK to `land_file` must be named `land` (not `land_file` or `land_id`) — Django adds `_id` suffix
- Use Django `JSONField` (PostgreSQL/CockroachDB → **JSONB**) for audit log old/new values — not plain `TEXT`
- Never store arrays as comma-separated strings — use proper FK tables or `ArrayField`
- All queries on large tables must have appropriate indexes — check with `EXPLAIN ANALYZE` before merging

---

## NOTIFICATION RULES

- Never send notifications synchronously in a request/response cycle — always via Celery
- Always log every notification attempt to `notification_log` table regardless of success/failure
- Failed notifications must be retried (max 3 times, 15 min intervals)
- WhatsApp is primary channel; SMS (Twilio) is fallback — implement fallback logic
- Never send raw phone numbers without country code — always format as `+91XXXXXXXXXX`

---

## NAMING CONVENTIONS

### Django
```python
# Models: PascalCase
class LegalCase, class HearingDocument, class PlanOfAction

# Variables / functions: snake_case
land_file, case_number, get_overdue_hearings()

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE_MB = 500
POA_DEADLINE_DAYS = 2

# URL names: kebab-case with module prefix
'land-list', 'legal-case-detail', 'task-create'

# App labels: lowercase, no hyphens
'land', 'legal', 'documents', 'tasks', 'users'
```

### React
```javascript
// Components: PascalCase
LandFileCard, HearingCalendar, FounderDashboard

// Hooks: camelCase with 'use' prefix
useLandFiles(), useCurrentUser(), useLegalCases()

// API functions: camelCase with verb prefix
fetchLandFiles(), createLegalCase(), uploadDocument()

// Files: kebab-case for pages, PascalCase for components
pages/land/land-list.jsx
components/LandFileCard.jsx
```

---

## WHAT TO ASK BEFORE WRITING CODE

Before writing any new feature, verify:

1. **Which land_file does this belong to?** Every record needs an FK to land_file unless it's a geography/user/system record.
2. **Which roles can see this?** Check the Access Matrix in the PRD before writing the ViewSet.
3. **Does this need an audit log?** All mutations do. Add to AuditMiddleware or log manually.
4. **Does this trigger a notification?** Check the notification triggers list in the HLD.
5. **Does this involve file upload?** Use the S3 pre-signed URL flow — not direct Django upload.
6. **Is this a delete?** It must be soft delete. Check for the `soft_delete()` method.

---

## PROJECT REFERENCES

| Document | Location | Purpose |
|----------|----------|---------|
| PRD.md | /docs/PRD.md | Full feature requirements and user stories |
| ARCHITECTURE.md | /docs/ARCHITECTURE.md | Tech stack, system design, infra setup |
| HLD.md | /docs/HLD.md | Data flows, ERD, compliance engine, notification design |
| IMPLEMENTATION_STATUS.md | /docs/IMPLEMENTATION_STATUS.md | What the repo implements today (detailed) |
| COMPLETED.md | /docs/COMPLETED.md | Shipped scope — team sync |
| BACKLOG.md | /docs/BACKLOG.md | Not done / partial — priorities and roles |
| COCKROACHDB_MIGRATIONS.md | /docs/COCKROACHDB_MIGRATIONS.md | CRDB DDL review + future migration checklist |
| DEV_DATABASE.md | /docs/DEV_DATABASE.md | When / why to reset local SQLite or Docker DB after pulls |
| rules.md | /docs/rules.md | This file — coding rules for AI agents |

---

*Last updated: April 2026 — Phase 1 active; Keycloak optional; local DB reset doc linked*
