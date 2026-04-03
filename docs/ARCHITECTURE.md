# System Architecture Document
# Land Intelligence Management Platform (LIMP)
**Version:** 1.0 | **Date:** March 2026

---

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Components](#3-system-components)
4. [Infrastructure & Deployment](#4-infrastructure--deployment)
5. [Backend Architecture](#5-backend-architecture)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Database Architecture](#7-database-architecture)
8. [Security Architecture](#8-security-architecture)
9. [Async & Background Jobs](#9-async--background-jobs)
10. [File Storage Architecture](#10-file-storage-architecture)
11. [API Design Conventions](#11-api-design-conventions)

---

## 1. Architecture Overview

LIMP follows a **monolithic Django backend with a decoupled React frontend** architecture. This is the correct choice for Phase 1–2 given team size, complexity of business logic, and the deeply relational data model. The backend exposes a REST API consumed by the React SPA.

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│   React SPA (Web)          React Native App (Phase 3)        │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS / REST API
┌──────────────────────────▼───────────────────────────────────┐
│                      AWS EC2 (Ubuntu)                        │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │   Nginx         │  │   Gunicorn      │                    |
│  │  (Reverse Proxy)│→ │  (WSGI Server)  │                    │
│  └─────────────────┘  └────────┬────────┘                    │
│                                │                             │
│  ┌─────────────────────────────▼──────────────────────────┐  │
│  │              Django Application                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │  Land    │ │  Legal   │ │ Document │ │  Task    │   │  │
│  │  │  App     │ │  App     │ │  App     │ │  App     │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Revenue  │ │ Survey   │ │  Users/  │ │Dashboard │   │  │
│  │  │  App     │ │  App     │ │  RBAC    │ │  App     │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────┐   ┌──────────────────┐                 │
│  │  Celery Worker   │   │   Celery Beat     │                │
│  │  (Async Tasks)   │   │  (Scheduler)      │                │
│  └──────────────────┘   └──────────────────┘                 │
└──────────────────────────────┬───────────────────────────────┘
                               │
                 ┌─────────────┼──────────────────┐
                 │             │                  │
            ┌──────────────┐  ┌──────────────┐   ┌──────────────┐
            │ CockroachDB  │  │    Redis     │   │   AWS S3     │
            │ (self-hosted)│  │Cache+broker  │   │(File Storage)│
            └──────────────┘  └──────────────┘   └──────────────┘
            ┌──────────────┐  ┌──────────────┐
            │    Kafka     │  │  Cassandra   │
            │   (events)   │  │ (audit copy) │
            └──────────────┘  └──────────────┘
                               │
                 ┌─────────────┼──────────────────┐
                 │             │                  │
            ┌────▼────┐  ┌─────▼─────┐   ┌───────▼──────┐
            │  Meta   │  │  Twilio / │   │   (Future)   │
            │WhatsApp │  │  MSG91    │   │   External   │
            │   API   │  │  SMS API  │   │     APIs     │
            └─────────┘  └───────────┘   └──────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend Framework | Django | 6.x | Core application logic, ORM, admin |
| API Layer | Django REST Framework (DRF) | 3.x | REST API endpoints |
| Authentication | djangorestframework-simplejwt | Latest | JWT token auth |
| Frontend | Next.js (App Router) + React | Latest stable | Web UI; Turbopack in local dev |
| Language (frontend) | TypeScript | strict | Type-safe UI and API client |
| Package managers | uv (Python) · pnpm (Node) | Latest | Locked dependencies, CI |
| State Management | Zustand | Latest | Auth/session and lightweight global state |
| Server state | TanStack React Query | Latest | API data fetching and cache |
| UI Components | shadcn/ui + Tailwind CSS | Latest | Enterprise UI (aligned with UI_UX_SPEC) |
| Primary OLTP database | **CockroachDB** (self-hosted) | Latest stable LTS | Distributed SQL, PostgreSQL wire protocol; Django uses `django.db.backends.postgresql` + `psycopg` |
| Legacy / reference | PostgreSQL | 16.x | Optional during migration; local dev may use SQLite without Docker |
| Event streaming | **Apache Kafka** | 3.x | Topic-based ordering for audit fan-out and future domain events |
| Log / high-volume audit store | **Apache Cassandra** | 5.x | Durable append-friendly store for audit rows replicated from Kafka |
| Cache / Celery broker | Redis | 7.x | Celery broker + cache (rate limits, etc.) |
| Async Task Queue | Celery | 5.x | Background jobs, Kafka publish, notifications |
| Task Scheduler | Celery Beat | 5.x | Cron-style scheduled jobs |
| File Storage | AWS S3 + django-storages | Latest | All binary file storage |
| Web Server | Gunicorn | Latest | WSGI production server |
| Reverse Proxy | Nginx | Latest | SSL termination, static files, proxy |
| WhatsApp | Meta Business API | Cloud API | Official WhatsApp notifications |
| SMS | Twilio / MSG91 | Latest | SMS fallback notifications |
| Containerisation | Docker + Docker Compose | Latest | Dev environment consistency |
| CI/CD | GitHub Actions | — | Automated test + deploy pipeline |
| OS | Ubuntu 22.04 LTS | — | AWS EC2 base OS |

### 2.1 Data platform — opinionated layout

**CockroachDB as primary OLTP:** Matches LIMP’s **relational** model (land hierarchy, legal FKs, RBAC) while giving **distributed SQL**, survivability, and horizontal scale on self-hosted hardware. Django talks to Cockroach via the **PostgreSQL** backend (`psycopg`); avoid Postgres-only DDL where Cockroach differs (e.g. some `SERIAL` patterns — use explicit types / migrations reviewed for CRDB).

**Kafka:** Used to **decouple** hot paths from long-term log storage and future subscribers (analytics, compliance exports, integrations). Today: **`limp.audit`** topic receives JSON payloads after each successful mutating API request (via Celery). Later: domain events (task assigned, hearing scheduled) can use additional topics with schemas.

**Cassandra:** Stores **append-oriented audit copies** keyed by day + `timeuuid` for scalable scans. It is **not** the source of truth for authorization; the **`AuditLog` row in Cockroach** remains the transactional record the app reads for admin/forensics in-app. Cassandra is for retention, analytics, and heavy read patterns.

**Flow (simplified):** `API → AuditMiddleware → AuditLog (CRDB) → Celery → Kafka → audit-consumer → Cassandra`.

**Local development:** `docker-compose.yml` runs single-node CockroachDB, Kafka (KRaft), Cassandra, Redis, API, Celery worker/beat, and `audit-consumer`. Without Docker, CI and laptop tests use **SQLite** and **skip** Kafka publish when `KAFKA_BOOTSTRAP_SERVERS` is unset.

---

## 3. System Components

### 3.1 Django Apps (Modules)

Each major feature domain is a separate Django app. This enforces separation of concerns and allows the team to work in parallel.

```
backend/                       # Django project root (repo: `/backend`)
├── config/                    # Project settings, urls, wsgi, asgi, Celery
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                  # Shared models, mixins, utils (AuditMixin, SoftDeleteMixin)
│   ├── users/                 # User model, RBAC, JWT auth, roles, permissions
│   ├── geography/             # District, Taluk, Hobli, Village master data
│   ├── land/                  # Land Master module
│   ├── legal/                 # Legal cases, hearings, compliance engine
│   ├── documents/             # Document vault, version control
│   ├── tasks/                 # Task management, notifications
│   ├── revenue/               # Revenue workflows, officer mapping (Phase 2)
│   ├── survey/                # Survey assignments, survey data (Phase 2)
│   ├── valuation/             # Valuation, market intelligence (Phase 2)
│   ├── notifications/         # WhatsApp + SMS dispatcher
│   ├── dashboard/             # Dashboard aggregation endpoints
│   ├── audit/                 # Audit log model and middleware (Postgres/Cockroach)
│   └── telemetry/             # Kafka publishers (e.g. audit fan-out); no ORM models
├── config/celery.py           # Celery application
└── manage.py
```

### 3.2 Frontend Structure

```
frontend/                      # Next.js App Router (repo: `/frontend`)
├── app/                       # Routes, layouts, providers
├── components/                # Shared UI (incl. shadcn-generated `components/ui`)
├── lib/
│   ├── api/                   # Axios client and (later) module API helpers
│   ├── stores/                # Zustand stores (e.g. auth)
│   └── utils.ts               # Shared utilities (cn, etc.)
└── public/
```

---

## 4. Infrastructure & Deployment

### 4.1 AWS EC2 Setup

```
EC2 Instance (Recommended: t3.medium for Phase 1, scale up as needed)
├── Ubuntu 22.04 LTS
├── Nginx (port 80/443)
│   ├── SSL via Let's Encrypt (Certbot)
│   ├── Serves React build (static files)
│   └── Proxies /api/* → Gunicorn (port 8000)
├── Gunicorn (Django WSGI, 4 workers)
├── Celery Worker (systemd service)
├── Celery Beat (systemd service)
└── Redis (localhost:6379)

Separate:
├── **CockroachDB** cluster (self-hosted or CRDB Cloud — primary OLTP; PostgreSQL wire protocol)
├── **Kafka** + **Cassandra** (optional in smallest deploys; recommended for audit fan-out and scale — see §2.1)
└── AWS S3 Bucket (file storage, private, signed URLs only)
```

### 4.2 Environment Variables

```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=
DATABASE_URL=

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Redis
REDIS_URL=redis://localhost:6379/0

# WhatsApp
WHATSAPP_API_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=

# SMS
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=480
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

### 4.3 Deployment Process (GitHub Actions)

```
Push to main branch
  → Run tests (pytest)
  → Build React frontend (npm run build)
  → SSH into EC2
  → Pull latest code
  → pip install requirements
  → python manage.py migrate
  → Collect static files
  → Restart Gunicorn + Celery
```

### 4.4 Nginx Configuration (simplified)

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    # Serve React frontend
    location / {
        root /var/www/limp/frontend/build;
        try_files $uri /index.html;
    }

    # Proxy API to Django
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Media files served via S3 signed URLs — not served from here
}
```

---

## 5. Backend Architecture

### 5.1 Core Mixins (apps/core/)

All models inherit from these shared base classes:

```python
# apps/core/models.py

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class AuditedModel(TimeStampedModel):
    created_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT)
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT)
    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def soft_delete(self, user):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    class Meta:
        abstract = True
```

### 5.2 RBAC Implementation

```python
# apps/users/permissions.py

class IsFounder(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'FOUNDER'

class IsInHouseAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['FOUNDER', 'IN_HOUSE_ADVOCATE']

class IsExternalAdvocate(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'EXTERNAL_ADVOCATE'

# Row-level: external advocate case scoping
class CaseScopedQueryset:
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'EXTERNAL_ADVOCATE':
            return qs.filter(assigned_advocates=user)
        return qs
```

### 5.3 Audit Middleware

```python
# apps/audit/middleware.py
# Logs every mutating request (POST/PUT/PATCH/DELETE) to AuditLog table
# Fields: user, action, model_name, object_id, old_value (JSON), new_value (JSON), ip_address, timestamp
```

---

## 6. Frontend Architecture

### 6.1 Route Guards

```jsx
// src/routes/ProtectedRoute.jsx
// Checks JWT token validity and user role before rendering
// Redirects to /login if unauthenticated
// Redirects to /403 if authenticated but insufficient role
```

### 6.2 API Layer

```javascript
// src/api/client.js
// Axios instance with:
//   - Base URL from env
//   - JWT token injected from Zustand store
//   - 401 interceptor → auto logout
//   - 403 interceptor → redirect to /403

// src/api/land.js     → land module API calls
// src/api/legal.js    → legal module API calls
// src/api/tasks.js    → task module API calls
// etc. — one file per module
```

### 6.3 Role-Based UI Rendering

```jsx
// src/components/RoleGuard.jsx
// Wraps UI elements — only renders children if user has required role
// Used for: action buttons, sensitive data fields, nav menu items
<RoleGuard roles={['FOUNDER', 'MANAGEMENT']}>
  <InvestorDataSection />
</RoleGuard>
```

---

## 7. Database Architecture

### 7.1 Core Schema Overview

```sql
-- Geography hierarchy
district (id, name, state)
taluk (id, name, district_id FK)
hobli (id, name, taluk_id FK)
village (id, name, hobli_id FK)

-- Land Master (central anchor table)
land_file (
  id, land_id (unique, generated),
  village_id FK, survey_number, hissa,
  extent_acres, extent_guntas, extent_sqft,
  classification, status,
  proposed_by, investment_min, investment_max,
  created_by FK, updated_by FK,
  is_deleted, deleted_at, deleted_by FK,
  created_at, updated_at
)

-- Users & RBAC
user (id, email, phone, name, role, is_active, last_login)
user_case_assignment (user_id FK, case_id FK)   -- external advocate scoping
user_task_assignment (user_id FK, task_id FK)    -- freelance surveyor scoping

-- Legal
legal_case (id, land_id FK, case_number, case_type, court, party_role,
            current_stage, status, opposite_advocate_name, opposite_advocate_contact,
            created_by FK, ...)
case_advocate (case_id FK, user_id FK, is_lead)
hearing (id, case_id FK, hearing_date, notes, next_date, created_by FK, ...)
hearing_document (id, hearing_id FK, doc_type, s3_key, uploaded_by FK, ...)
plan_of_action (id, hearing_id FK, s3_key, uploaded_by FK, uploaded_at,
                status [PENDING/SUBMITTED/OVERDUE], ...)
legal_opinion (id, case_id FK, s3_key, source, uploaded_by FK, ...)

-- Documents
document_type (id, name, description)
land_document (id, land_id FK, doc_type_id FK, status, current_version,
               created_by FK, ...)
document_version (id, land_document_id FK, version_number, s3_key,
                  uploaded_by FK, uploaded_at, notes)

-- Tasks
task (id, title, description, land_id FK (nullable), assigned_to FK,
      created_by FK, due_date, priority, status, module,
      created_at, updated_at, is_deleted, ...)

-- Notifications
notification_log (id, user_id FK, channel [WHATSAPP/SMS], message,
                  status [SENT/FAILED/PENDING], sent_at, error_message)

-- Audit
audit_log (id, user_id FK, action, model_name, object_id,
           old_value JSONB, new_value JSONB, ip_address, timestamp)
```

### 7.2 Indexing Strategy

```sql
-- High-frequency query indexes
CREATE INDEX idx_land_file_village ON land_file(village_id);
CREATE INDEX idx_land_file_status ON land_file(status);
CREATE INDEX idx_land_file_deleted ON land_file(is_deleted);
CREATE INDEX idx_legal_case_land ON legal_case(land_id);
CREATE INDEX idx_hearing_date ON hearing(hearing_date);
CREATE INDEX idx_task_assigned ON task(assigned_to);
CREATE INDEX idx_task_status ON task(status);
CREATE INDEX idx_audit_object ON audit_log(model_name, object_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
```

### 7.3 Soft Delete Pattern

All querysets filter `is_deleted=False` by default via a custom Manager:

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
```

### 7.4 CockroachDB and Django migrations

LIMP app migrations are reviewed for **CockroachDB** (PostgreSQL protocol) compatibility. Summary, per-app notes, and a **pre-merge checklist** for future DDL live in **[`docs/COCKROACHDB_MIGRATIONS.md`](COCKROACHDB_MIGRATIONS.md)**. Re-run `sqlmigrate` against a live CRDB when adding migrations.

---

## 8. Security Architecture

### 8.1 Authentication Flow

```
1. POST /api/auth/login/ → {email, password}
2. Django validates credentials
3. Returns {access_token (8h), refresh_token (7d)}
4. Frontend stores tokens in memory (access) and httpOnly cookie (refresh)
5. Every API request: Authorization: Bearer <access_token>
6. Token expired → POST /api/auth/refresh/ → new access token
7. Refresh token expired → force re-login
```

### 8.2 External Advocate Token Scoping

```python
# JWT payload for external advocates includes case_ids claim
{
  "user_id": 42,
  "role": "EXTERNAL_ADVOCATE",
  "case_ids": [101, 205],   # injected at login time from DB
  "exp": ...
}

# Every legal endpoint for external advocates validates:
# requested_case_id in token.case_ids
```

### 8.3 S3 File Security

- All S3 buckets are **private** (no public access)
- Files served via **pre-signed URLs** with 15-minute expiry
- File upload goes via **pre-signed upload URL** (client uploads directly to S3, no file passes through Django server)
- S3 bucket policy denies all public GetObject requests

### 8.4 Sensitive Data Encryption

```python
# Using django-encrypted-fields or pgcrypto
# Encrypted at rest:
aadhaar_number = EncryptedCharField(max_length=12)
pan_number = EncryptedCharField(max_length=10)
bank_account_number = EncryptedCharField(max_length=20)
investor_capacity_min = EncryptedDecimalField()
```

---

## 9. Async & Background Jobs

### 9.1 Celery Task Structure

```python
# apps/tasks/celery_tasks.py
@shared_task
def send_task_assignment_notification(task_id): ...

@shared_task
def check_overdue_tasks(): ...          # runs hourly

@shared_task
def send_daily_task_digest(): ...       # runs at 9:00 AM daily

# apps/legal/celery_tasks.py
@shared_task
def create_hearing_compliance_tasks(): ...  # runs daily — checks hearings in 5 days
@shared_task
def send_poa_reminder(hearing_id): ...     # runs at hearing-3 days
@shared_task
def check_poa_overdue(): ...               # runs hourly
@shared_task
def escalate_overdue_poa(hearing_id): ...
```

### 9.2 Celery Beat Schedule

```python
# celery_app.py
CELERY_BEAT_SCHEDULE = {
    'check-overdue-tasks': {
        'task': 'apps.tasks.celery_tasks.check_overdue_tasks',
        'schedule': crontab(minute=0),          # every hour
    },
    'daily-task-digest': {
        'task': 'apps.tasks.celery_tasks.send_daily_task_digest',
        'schedule': crontab(hour=9, minute=0),  # 9:00 AM daily
    },
    'hearing-compliance-check': {
        'task': 'apps.legal.celery_tasks.create_hearing_compliance_tasks',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
    'poa-overdue-check': {
        'task': 'apps.legal.celery_tasks.check_poa_overdue',
        'schedule': crontab(minute=0),          # every hour
    },
}
```

---

## 10. File Storage Architecture

### 10.1 S3 Key Structure

```
limp-production/
├── land/{land_id}/
│   ├── documents/{doc_type}/{version}_{filename}
│   └── survey/{survey_id}/
│       ├── photos/
│       ├── sketches/
│       ├── drone_videos/
│       └── fmb_extracts/
├── legal/{case_id}/
│   ├── plaint/v{n}_{filename}
│   ├── written_statement/v{n}_{filename}
│   ├── hearings/{hearing_id}/
│   │   ├── orders/
│   │   ├── audio/
│   │   └── video/
│   └── opinions/
├── identity/{land_id}/{seller_id}/   # Phase 3 — KYC docs
│   └── (encrypted at S3 level too)
```

### 10.2 Upload Flow

```
1. Frontend requests pre-signed upload URL from Django
   POST /api/files/presigned-upload/
   → { "s3_key": "...", "upload_url": "https://s3.amazonaws.com/..." }

2. Frontend uploads file directly to S3 using the pre-signed URL
   PUT {upload_url} with file binary

3. Frontend confirms upload to Django
   POST /api/files/confirm-upload/
   → Django creates DB record with s3_key

4. File retrieval: Django generates pre-signed download URL (15 min expiry)
   GET /api/files/{file_id}/download/
   → { "download_url": "https://s3.amazonaws.com/..." }
```

---

## 11. API Design Conventions

### 11.1 URL Patterns

```
/api/v1/auth/login/
/api/v1/auth/refresh/
/api/v1/auth/logout/

/api/v1/land/                       GET (list), POST (create)
/api/v1/land/{land_id}/             GET, PUT, PATCH, DELETE (soft)
/api/v1/land/{land_id}/documents/   GET (document checklist for land)

/api/v1/legal/cases/                GET, POST
/api/v1/legal/cases/{id}/           GET, PUT, PATCH
/api/v1/legal/cases/{id}/hearings/  GET, POST
/api/v1/legal/hearings/{id}/poa/    GET, POST (Plan of Action)

/api/v1/tasks/                      GET, POST
/api/v1/tasks/{id}/                 GET, PUT, PATCH

/api/v1/dashboard/summary/          GET (Founder KPI summary)
/api/v1/dashboard/hearings-today/   GET
/api/v1/dashboard/overdue-tasks/    GET
```

### 11.2 Response Format

```json
// Success
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "total": 42, "page_size": 20 }
}

// Error
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have access to this resource."
  }
}
```

### 11.3 Pagination

All list endpoints are paginated. Default page size: 20. Max: 100.

```
GET /api/v1/land/?page=2&page_size=20&status=active&district=bangalore_rural
```

---

*Document Version: 1.0 | Last Updated: March 2026*
