# High Level Design (HLD)
# Land Intelligence Management Platform (LIMP)
**Version:** 1.0 | **Date:** March 2026

---

## Table of Contents
1. [System Context](#1-system-context)
2. [Module Interaction Map](#2-module-interaction-map)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Database Entity Relationships](#4-database-entity-relationships)
5. [Compliance Engine Design](#5-compliance-engine-design)
6. [Notification System Design](#6-notification-system-design)
7. [RBAC Design Detail](#7-rbac-design-detail)
8. [Phase 1 Deliverable Checklist](#8-phase-1-deliverable-checklist)

---

## 1. System Context

### 1.1 What the system replaces / consolidates

| Currently done via | Replaced by |
|-------------------|-------------|
| WhatsApp groups for legal updates | Legal module + task notifications |
| Excel sheets for land records | Land Master module |
| Physical document folders | Document Vault |
| Verbal advocate follow-ups | Compliance Engine (auto) |
| Founder calling team for updates | Founder Dashboard |
| Spreadsheets for revenue tracking | Revenue Workflow module |
| No surveyor data system | Survey module |

### 1.2 External Systems

| External System | Direction | Purpose |
|----------------|-----------|---------|
| Meta WhatsApp Business API | Outbound | Task notifications, reminders, escalations |
| Twilio / MSG91 | Outbound | SMS fallback notifications |
| AWS S3 | Read/Write | All file and document storage |
| AWS EC2 | Hosting | Application server |

---

## 2. Module Interaction Map

```
                          ┌─────────────────┐
                          │   LAND MASTER   │ ← Central anchor
                          │   (land_file)   │
                          └────────┬────────┘
                                   │ FK reference (mandatory)
              ┌────────────────────┼────────────────────────────┐
              │                    │                             │
    ┌─────────▼──────┐  ┌─────────▼──────┐  ┌────────────────▼─┐
    │  LEGAL MODULE  │  │ DOCUMENT VAULT │  │  REVENUE MODULE  │
    │  Cases         │  │  Checklist     │  │  Workflows        │
    │  Hearings      │  │  Versions      │  │  Officer mapping  │
    │  Compliance    │  │  Audit log     │  │  Days pending     │
    └────────┬───────┘  └───────┬────────┘  └────────┬─────────┘
             │                  │                     │
    ┌────────▼───────┐          │          ┌──────────▼────────┐
    │  TASK MODULE   │◄─────────┴──────────┤  SURVEY MODULE    │
    │  Assignments   │  (tasks created     │  Assignments      │
    │  Notifications │   by all modules)   │  Ground data      │
    │  Escalations   │                     │  Uploads          │
    └────────┬───────┘                     └───────────────────┘
             │
    ┌────────▼───────┐          ┌──────────────────────────────┐
    │ NOTIFICATIONS  │          │      DASHBOARD MODULE        │
    │  WhatsApp      │          │  Aggregates from all modules │
    │  SMS           │          │  KPIs, alerts, calendar      │
    └────────────────┘          └──────────────────────────────┘
```

---

## 3. Data Flow Diagrams

### 3.1 Land File Creation Flow

```
Founder / Management
        │
        ▼
  Fill land form
  (District → Taluk → Hobli → Village → Sy No → Hissa → Extent → Classification)
        │
        ▼
  POST /api/v1/land/
        │
        ▼
  Django validates fields
  Generates Land ID (LIMP-YYYY-NNNN)
        │
        ▼
  Saves to land_file table
  Creates audit_log entry
        │
        ▼
  Returns land_id + success
        │
        ▼
  Frontend redirects to Land File detail page
  (All sub-modules now show as empty/pending for this land)
```

### 3.2 Legal Case + Hearing Flow

```
In-House Advocate
        │
        ▼
  Create case linked to land_id
  Assign external advocate(s)
        │
        ▼
  Django creates legal_case record
  Creates case_advocate link records
  Celery: sends assignment notification to external advocate
        │
        ▼
  Add hearing date
        │
        ▼
  Django creates hearing record
  Celery Beat: checks daily — hearing in 5 days?
        │
        ▼
  D-5: Auto-create POA compliance task assigned to advocate
  D-3: Send WhatsApp + SMS reminder to advocate
        │
        ├─── Advocate uploads POA ──────────────────────────────┐
        │                                                        │
        │    POA not uploaded by D-2                            │
        │                                                        │
        ▼                                                        ▼
  Status → OVERDUE                                    Status → SUBMITTED
  Escalation notification to in-house supervisor     Compliance task → DONE
  Founder dashboard alert triggered                  Audit log entry
  Audit log entry
```

### 3.3 Document Upload Flow

```
Authorised User
        │
        ▼
  Select land file → Documents tab
  Click upload on a document type
        │
        ▼
  Frontend: POST /api/v1/files/presigned-upload/
  { land_id, doc_type, filename }
        │
        ▼
  Django generates S3 pre-signed upload URL
  Returns { s3_key, upload_url }
        │
        ▼
  Frontend: PUT {upload_url} with file (direct to S3)
  (File never touches Django server)
        │
        ▼
  Frontend: POST /api/v1/files/confirm-upload/
  { s3_key, land_document_id }
        │
        ▼
  Django creates document_version record
  Increments version number
  Updates land_document status
  Creates audit_log entry
        │
        ▼
  Document appears in vault with version history
```

### 3.4 Task Creation + Notification Flow

```
Any Module (Legal/Revenue/Survey/Manual)
        │
        ▼
  Task created (assigned_to, due_date, land_id, module)
        │
        ▼
  Saved to task table
        │
        ▼
  Celery: send_task_assignment_notification.delay(task_id)
        │
        ▼
  Notification worker:
    1. Fetch user phone from DB
    2. POST to Meta WhatsApp API
    3. Log result to notification_log
    4. If WhatsApp fails → fallback to SMS (Twilio)
    5. If SMS fails → log failure, retry in 15 min (max 3 retries)
        │
        ▼
  Celery Beat (hourly): check_overdue_tasks
    → Any task where due_date < now AND status != COMPLETED
    → Status → OVERDUE
    → Escalation notification to creator/supervisor
```

---

## 4. Database Entity Relationships

### 4.1 Core ERD (Phase 1)

```
district ──< taluk ──< hobli ──< village ──< land_file
                                                  │
                    ┌─────────────────────────────┼─────────────────────────┐
                    │                             │                         │
               legal_case                  land_document               task
                    │                             │                         │
           ┌────────┴───────┐            document_version          notification_log
           │                │
       hearing         case_advocate ──> user
           │
   ┌───────┴──────────┐
plan_of_action   hearing_document


user ──< audit_log (every action on every object)
```

### 4.1.1 Audit event pipeline (implementation)

Mutating API requests write **`audit_log` in the primary database (CockroachDB in production)**. A **Celery** task publishes a compact JSON message to **Kafka** topic `limp.audit`. A dedicated **consumer** process appends rows to **`limp.audit_logs` in Cassandra** for scalable retention and analytics. The primary `audit_log` table remains the source of truth for product features; Cassandra is the long-horizon / high-volume copy.

### 4.2 Key Relationship Rules

| Relationship | Type | Rule |
|---|---|---|
| land_file → village | Many-to-One | Mandatory FK; village must exist in master |
| legal_case → land_file | Many-to-One | Mandatory FK; case cannot exist without land |
| hearing → legal_case | Many-to-One | Mandatory FK |
| plan_of_action → hearing | One-to-One | One POA per hearing |
| land_document → land_file | Many-to-One | Mandatory FK |
| document_version → land_document | Many-to-One | Versions stack on the document record |
| task → land_file | Many-to-One | Optional FK (some admin tasks not land-linked) |
| task → user (assigned_to) | Many-to-One | Mandatory — every task must be assigned |
| audit_log → user | Many-to-One | Mandatory — every audit entry has an actor |
| Legal / documents (APIs) | **Partial** | Document RBAC ViewSets done; Legal APIs pending |
| Tasks / Notifications | **Part 2** | Dashboard stats API in progress (B10); Foundation Done |
| Revenue / Workflows | **Part 2** | Automation & Task hooks in progress (B17); Part 1 Done |
| S3 presigned uploads | **Part 2** | Identity/KYC and analytics in progress (B16); Foundation Done |
| Identity / KYC | **In Progress** | IdentityDocument model & masking logic |

---

## 5. Compliance Engine Design

### 5.1 State Machine — Plan of Action

```
Hearing Created
      │
      ▼
  POA_REQUIRED (default state when hearing is created)
      │
      │ D-5: Celery job creates compliance task
      ▼
  TASK_CREATED
      │
      ├────────────────────────────────────────────┐
      │                                            │
      │ Advocate uploads POA                       │ D-2 passes, no upload
      ▼                                            ▼
  SUBMITTED ──────────────────────────────►  OVERDUE
  (compliance task = DONE)                  (escalation fired)
                                            (Founder dashboard alert)
                                            (audit log entry)
```

### 5.2 Escalation Chain

```
Level 1: WhatsApp + SMS to assigned advocate (D-3 reminder)
Level 2: If overdue (D-2) → WhatsApp to in-house advocate supervisor
Level 3: Founder dashboard alert badge (red)
Level 4: Daily digest includes overdue POAs until resolved
```

### 5.3 Celery Jobs for Compliance

```python
# Runs daily at 8:00 AM
def create_hearing_compliance_tasks():
    hearings_in_5_days = Hearing.objects.filter(
        hearing_date=date.today() + timedelta(days=5),
        poa__isnull=True  # no POA record yet
    )
    for hearing in hearings_in_5_days:
        Task.objects.create(
            title=f"Plan of Action required: {hearing.case.case_number}",
            assigned_to=hearing.case.lead_advocate,
            due_date=hearing.hearing_date - timedelta(days=2),
            module='LEGAL',
            land=hearing.case.land
        )
        # triggers immediate WhatsApp notification via task creation signal

# Runs hourly
def check_poa_overdue():
    threshold = date.today() + timedelta(days=2)
    overdue_hearings = Hearing.objects.filter(
        hearing_date=threshold,
        poa__isnull=True
    )
    for hearing in overdue_hearings:
        hearing.poa_status = 'OVERDUE'
        hearing.save()
        escalate_overdue_poa.delay(hearing.id)
```

---

## 6. Notification System Design

### 6.1 Notification Service Architecture

```python
# apps/notifications/service.py

class NotificationService:
    def send(self, user_id, message, channel='WHATSAPP'):
        user = User.objects.get(id=user_id)
        log = NotificationLog.objects.create(
            user=user,
            channel=channel,
            message=message,
            status='PENDING'
        )
        try:
            if channel == 'WHATSAPP':
                self._send_whatsapp(user.phone, message)
            else:
                self._send_sms(user.phone, message)
            log.status = 'SENT'
            log.sent_at = timezone.now()
        except Exception as e:
            log.status = 'FAILED'
            log.error_message = str(e)
            # Schedule retry
            retry_notification.apply_async(args=[log.id], countdown=900)  # 15 min
        finally:
            log.save()

    def _send_whatsapp(self, phone, message):
        # Meta Cloud API call
        requests.post(
            f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
            headers={"Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }
        )
```

### 6.2 Notification Templates

| Event | Channel | Message Template |
|-------|---------|-----------------|
| Task assigned | WhatsApp + SMS | "New task assigned: {title}. Due: {due_date}. View: {link}" |
| POA reminder (D-3) | WhatsApp + SMS | "Reminder: Plan of Action for case {case_no} hearing on {date} is due by {deadline}" |
| POA overdue | WhatsApp + SMS | "URGENT: Plan of Action for {case_no} is overdue. Hearing: {date}" |
| Task overdue | WhatsApp | "Overdue task: {title} was due on {due_date}" |
| Daily digest | WhatsApp | "Good morning. You have {n} pending tasks today. Hearings: {list}" |
| Court order uploaded | WhatsApp | "Court order uploaded for case {case_no} by {advocate_name}" |

---

## 7. RBAC Design Detail

### 7.1 Role Constants

```python
class UserRole(models.TextChoices):
    FOUNDER = 'FOUNDER', 'Founder / Super Admin'
    MANAGEMENT = 'MANAGEMENT', 'Management'
    IN_HOUSE_ADVOCATE = 'IN_HOUSE_ADVOCATE', 'In-House Advocate'
    EXTERNAL_ADVOCATE = 'EXTERNAL_ADVOCATE', 'External Advocate'
    REVENUE_TEAM = 'REVENUE_TEAM', 'Revenue Team'
    SURVEYOR_INHOUSE = 'SURVEYOR_INHOUSE', 'Surveyor (In-House)'
    SURVEYOR_FREELANCE = 'SURVEYOR_FREELANCE', 'Surveyor (Freelance)'
    FIELD_STAFF = 'FIELD_STAFF', 'Field Staff'
```

### 7.2 Permission Matrix Implementation

```python
# Each ViewSet defines permission_classes based on action
class LegalCaseViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewLegalCases()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsInHouseAdvocateOrAbove()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsFounder()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = LegalCase.objects.filter(is_deleted=False)
        # External advocates only see their assigned cases
        if user.role == UserRole.EXTERNAL_ADVOCATE:
            qs = qs.filter(assigned_advocates=user)
        return qs
```

### 7.3 JWT Payload Design

```json
// Standard user
{
  "user_id": 10,
  "role": "MANAGEMENT",
  "name": "Ravi Kumar",
  "exp": 1234567890
}

// External advocate — case-scoped
{
  "user_id": 42,
  "role": "EXTERNAL_ADVOCATE",
  "case_ids": [101, 205, 318],
  "exp": 1234567890
}

// Freelance surveyor — task-scoped
{
  "user_id": 67,
  "role": "SURVEYOR_FREELANCE",
  "task_ids": [88, 92],
  "exp": 1234567890
}
```

---

## 8. Phase 1 Deliverable Checklist

### Backend
- [x] Django project scaffolded with all apps created
- [x] **CockroachDB** (or PostgreSQL-compatible `DATABASE_URL`) connected and migrations running
- [x] Custom User model with role field
- [x] JWT auth endpoints (login, refresh, logout)
- [x] Geography master data seeded (Karnataka districts/taluks/hoblis/villages)
- [x] Land Master CRUD API- **Phase 1 domain scaffold (backend):** Django apps `legal`, `revenue` models added. `revenue` app Part 1 fully implemented with Officer profiles, Government Workflow logic, and `days_pending` calculation. `documents` app foundation fully implemented with S3 pre-signed upload/download services and `LandDocumentChecklist`. `tasks` app foundation fully implemented with Task APIs, RBAC, NotificationLog idempotency, and Celery beat schedules (WhatsApp stubbed). Routes composed via `config/api_v1_urls.py`. **Phase 1 Part 1 is 100% complete; transitioning to Part 2 (Dashboard, KYC, & Revenue Automation).**
- [x] Legal Case CRUD API with external advocate scoping
- [x] Hearing CRUD API with POA compliance engine
- [x] Document Vault API with S3 pre-signed upload/download
- [x] Document version tracking
- [x] Task CRUD API with role-based visibility
- [x] Revenue Workflow CRUD API with Officer mapping (§3.1, §3.2)
- [x] Audit log middleware capturing all mutations
- [x] Celery + Redis configured
- [x] Celery Beat jobs: overdue task check, POA compliance, daily digest
- [x] WhatsApp notification service (Meta API)
- [x] SMS fallback (Twilio/MSG91)
- [x] Dashboard summary aggregation endpoint
- [x] Rate limiting on login endpoint
- [x] All endpoints return standardised response format

### Frontend
- [ ] Next.js app scaffolded (App Router; TypeScript strict)
- [ ] Axios client with JWT injection and interceptors
- [ ] Login page with JWT storage
- [ ] Route guards with role-based access
- [ ] Land Master: list, create, detail pages
- [ ] Legal: case list, case detail, hearing list, POA upload
- [ ] Documents: checklist view, upload, version history
- [ ] Tasks: my tasks view, create task
- [ ] Founder Dashboard: KPI cards, hearings today, overdue tasks, activity feed
- [ ] Travel Mode toggle on dashboard
- [ ] RoleGuard component used on all sensitive UI elements
- [ ] Responsive layout (desktop-first for Phase 1)

### Infrastructure
- [ ] EC2 instance provisioned (Ubuntu 22.04)
- [ ] **CockroachDB** running (self-hosted cluster or CRDB Cloud); **Kafka** + **Cassandra** for audit pipeline where required
- [ ] Redis running
- [ ] Nginx configured with SSL
- [ ] Gunicorn running as systemd service
- [ ] Celery worker running as systemd service
- [ ] Celery Beat running as systemd service
- [ ] S3 bucket created with correct private policy
- [ ] Environment variables set in production
- [ ] GitHub Actions CI/CD pipeline running
- [ ] Daily DB backup to S3 configured

---

*Document Version: 1.0 | Last Updated: March 2026*

*Engineering tracking:* [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) · [COMPLETED.md](COMPLETED.md) · [BACKLOG.md](BACKLOG.md) · [COCKROACHDB_MIGRATIONS.md](COCKROACHDB_MIGRATIONS.md).
