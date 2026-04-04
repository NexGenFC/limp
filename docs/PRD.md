# Product Requirements Document (PRD)
# Land Intelligence Management Platform (LIMP)
**Client:** Abhivruddhi Ventures  
**Version:** 1.0  
**Date:** March 2026  
**Status:** Approved — Development Active

---

## Table of Contents
1. [Product Overview](#1-product-overview)
2. [Goals & Success Metrics](#2-goals--success-metrics)
3. [Users & Roles](#3-users--roles)
4. [Phase 1 — Feature Requirements](#4-phase-1--feature-requirements)
5. [Phase 2 — Feature Requirements](#5-phase-2--feature-requirements)
6. [Phase 3 — Feature Requirements](#6-phase-3--feature-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Constraints & Assumptions](#8-constraints--assumptions)

---

## 1. Product Overview

### 1.1 What This Is
The Land Intelligence Management Platform (LIMP) is the **core operating system** for Abhivruddhi Ventures — a Karnataka-based real estate, litigated land acquisition, and land development company.

This is **not** a CRM, listing platform, or ERP. It is a mission-critical operational platform that consolidates:
- Land intelligence and master records
- Legal case management and compliance
- Government revenue workflow tracking
- Survey and ground reality data
- Document vault and compliance engine
- Investor and capital intelligence
- Task management and team accountability
- Founder decision dashboard

### 1.2 Core Design Philosophy
> **Every land parcel is a Master File. All information must be anchored to it. Nothing exists in isolation.**

- Every entity in the system (legal case, document, survey task, revenue workflow, valuation) has a mandatory FK reference to a Land Master record.
- The system must preserve institutional memory even if people leave.
- The founder must be able to monitor all operations 24×7 from anywhere.

### 1.3 Scope Summary by Phase

| Phase | Name | Core Focus |
|-------|------|------------|
| Phase 1 | Foundation | Land records, legal, documents, RBAC, tasks, basic dashboard |
| Phase 2 | Advanced Workflow | Survey, revenue workflows, WhatsApp automation, valuation intelligence |
| Phase 3 | Expansion | Mobile app, analytics, intelligence layer |

---

## 2. Goals & Success Metrics

| Goal | Metric |
|------|--------|
| Centralise all land data | 100% of land files have all linked records — zero orphaned data |
| Legal compliance | 100% of hearing Plan of Actions uploaded on time or escalated |
| Access control | Zero cross-role data leakage in audit testing |
| Task accountability | All tasks assigned with notifications; overdue rate tracked |
| Founder visibility | Founder dashboard loads within 3 seconds; all KPIs visible at a glance |
| System uptime | 99.5% uptime SLA post-deployment |

---

## 3. Users & Roles

### 3.1 Role Definitions

| Role | Description | Count (approx.) |
|------|-------------|-----------------|
| Founder / Super Admin | Full system access; owns all data and settings | 1 |
| Management | Operational access; no investor/capital data | 2–3 |
| In-House Advocate | Full legal module; supervises all cases | 3 |
| External Advocate | Restricted; sees only assigned cases | 10–15 |
| Revenue Team | Revenue & government workflow module only | 2–4 |
| Surveyor (In-House) | Survey module — all assignments | 1–2 |
| Surveyor (Freelance) | Task-scoped only; no cross-visibility | 6–8 |
| Field Staff | Assigned tasks only | Variable |

### 3.2 Access Matrix

| Module | Founder | Management | In-House Adv. | External Adv. | Revenue | Surveyor (IH) | Surveyor (FL) | Field Staff |
|--------|---------|------------|---------------|---------------|---------|----------------|----------------|-------------|
| Land Master | ✅ Full | ✅ Full | ✅ Read | ❌ Case fields only | ✅ Read | ✅ Read | ❌ | ❌ |
| Legal Module | ✅ Full | ✅ Read | ✅ Full | ✅ Own cases only | ❌ | ❌ | ❌ | ❌ |
| Revenue Module | ✅ Full | ✅ Read | ❌ | ❌ | ✅ Full | ❌ | ❌ | ❌ |
| Survey Module | ✅ Full | ✅ Read | ❌ | ❌ | ❌ | ✅ Full | ✅ Own tasks | ❌ |
| Document Vault | ✅ Full | ✅ Read | ✅ Legal docs | ✅ Case docs only | ✅ Revenue docs | ✅ Survey docs | ❌ | ❌ |
| Investor Module | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Task Module | ✅ Full | ✅ Own + team | ✅ Own tasks | ✅ Own tasks | ✅ Own tasks | ✅ Own tasks | ✅ Own tasks | ✅ Own tasks |
| Dashboard | ✅ Full | ✅ Partial | ✅ Legal KPIs | ❌ | ✅ Revenue KPIs | ✅ Survey KPIs | ❌ | ❌ |
| Valuation / Market | ✅ Full | ✅ Read | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Identity / KYC | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 4. Phase 1 — Feature Requirements

### 4.1 Land Master Module

**Purpose:** Central record for every land parcel. Anchor for all other modules.

**Fields:**
- `land_id` — auto-generated unique identifier (e.g., `LIMP-2026-0001`)
- District, Taluk, Hobli, Village (FK-linked hierarchy)
- Survey Number (Sy No), Hissa
- Extent — Acres, Guntas, Sq Ft
- Classification — Agricultural / Converted / Approved Site
- Project proposed by (user reference)
- Expected investment — Min (₹) / Max (₹)
- Status — Active / Under Negotiation / Committed / Closed
- Created by, Created at, Last updated by, Last updated at

**Hierarchy:**
```
District
  └── Taluk
        └── Hobli
              └── Village
                    └── Land File (Sy No + Hissa)
```

**User Stories:**
- As Founder, I can create a new land file with all identifiers and it gets a unique Land ID.
- As Founder, I can search/filter land files by district, taluk, village, classification, or status.
- As Management, I can view all land files but cannot modify investment or investor data.
- As any user, I see only land files relevant to my role.

**Acceptance Criteria:**
- [ ] Land ID is system-generated, unique, non-editable after creation
- [ ] Village → Hobli → Taluk → District hierarchy is enforced via FK, not free text
- [ ] Soft delete only — no land file can be hard deleted
- [ ] Audit log entry created on every field change

---

### 4.2 Legal Case Management Module

**Purpose:** Court-grade case tracking for all legal matters linked to land files.

**Case Fields:**
- Land file reference (FK)
- Case number, case type (OS / MFA / WP / etc.)
- Court jurisdiction — Civil Court / District Court / High Court / Tribunal
- Party role — Plaintiff / Defendant / Appellant / Respondent
- Current stage
- Assigned advocate(s) — FK to user table
- Opposite advocate name, firm, contact
- Next hearing date
- Case status — Active / Stayed / Disposed / Won / Lost

**Document Uploads (per case):**
- Plaint (version-controlled)
- Written Statement (version-controlled)
- Court orders (per hearing)
- Previous legal opinions

**Hearing Records:**
- Hearing date
- What happened (notes)
- Next date set
- Audio summary upload
- Video summary upload
- Court order upload

**Compliance Engine:**
- For every hearing, assigned advocate must upload Plan of Action ≥ 2 days prior
- System auto-creates a compliance task 5 days before hearing
- WhatsApp + SMS reminder sent 3 days before deadline
- If not uploaded 2 days before hearing → status = OVERDUE → escalate to in-house supervisor → notify Founder dashboard
- All compliance events logged with timestamp

**Calendar:**
- All-cases calendar view (daily / weekly / monthly)
- Filter by advocate, court, land file, case type

**User Stories:**
- As Founder, I can see all active cases, their stages, and next hearing dates in one view.
- As In-House Advocate, I can supervise all cases and review compliance status.
- As External Advocate, I can only see my assigned cases and upload my Plan of Action.
- As Founder, I receive an alert if any advocate's Plan of Action is overdue.

**Acceptance Criteria:**
- [ ] External advocate login shows only their assigned case(s) — enforced at API level
- [ ] Version history maintained for plaint and written statement uploads
- [ ] Compliance task auto-created 5 days before every hearing
- [ ] Escalation triggered automatically — no manual step required
- [ ] Calendar shows correct upcoming hearings with advocate names

---

### 4.3 Document Vault

**Purpose:** Centralised, version-controlled document store for every land file.

**Document Checklist (per land file):**

| Document | Status Options |
|----------|----------------|
| RTC (Record of Rights) | Certified Obtained / Applied & Pending / Not Applicable |
| EC (Encumbrance Certificate) | Certified Obtained / Applied & Pending / Not Applicable |
| Phodi Sketch | Certified Obtained / Applied & Pending / Not Applicable |
| Tippani | Certified Obtained / Applied & Pending / Not Applicable |
| Grant Order | Certified Obtained / Applied & Pending / Not Applicable |
| Court Certified Copies | Certified Obtained / Applied & Pending / Not Applicable |
| Mutation Extract | Certified Obtained / Applied & Pending / Not Applicable |
| Sale Deed / Agreement | Certified Obtained / Applied & Pending / Not Applicable |

**Features:**
- Upload new version of any document — previous versions retained
- View version history with uploader name and timestamp
- No hard delete — only soft archive
- Audit log on every upload, view, and status change
- Role-based visibility — each role sees only their relevant documents

**User Stories:**
- As Founder, I can see the document completeness status for every land file at a glance.
- As any authorised user, I can upload a new document version and the old one is preserved.
- As Founder, I can see who uploaded what document and when.

**Acceptance Criteria:**
- [ ] Every document upload creates a version record (version number, uploader, timestamp)
- [ ] Old versions never deleted — accessible via version history
- [ ] Document checklist completion % shown per land file
- [ ] Audit log captures upload, view, and status change events

---

### 4.4 Role-Based Access Control (RBAC)

**Purpose:** Enforce access boundaries at the API level for all 8 user roles.

**Requirements:**
- Each user belongs to exactly one role
- Role determines which API endpoints are accessible
- Role determines which data rows are visible (row-level security)
- JWT tokens issued on login, contain role claim
- Every API endpoint validates role claim before serving data
- External advocate tokens additionally scoped to case ID list
- Freelance surveyor tokens scoped to task ID list
- Access token: short-lived (default 10 minutes, env-configurable); refresh token: N days (env-configurable); client refreshes access automatically; optional Keycloak IdP for MFA / SSO
- All login events logged (user, IP, timestamp, success/failure)

**Acceptance Criteria:**
- [ ] Attempting to access a restricted endpoint returns 403, not 404
- [ ] External advocate cannot fetch any land file not linked to their case
- [ ] All role permission changes logged with who changed it and when
- [ ] Brute force protection on login (rate limiting after 5 failed attempts)

---

### 4.5 Task Management System

**Purpose:** Every operational activity is a task. Nothing exists outside the task system.

**Task Fields:**
- Title, description
- Assigned to (user FK)
- Created by (user FK)
- Land file reference (FK — optional for admin tasks)
- Due date
- Priority — High / Medium / Low
- Status — Pending / In Progress / Completed / Overdue
- Module reference (Legal / Revenue / Survey / General)

**Notification Rules:**
- Task created → WhatsApp + SMS to assignee immediately
- Daily reminder at 9:00 AM for all pending tasks due that day
- Task overdue → escalation notification to creator and supervisor
- Task completed → notification to creator

**User Stories:**
- As Founder, I can see all tasks across all users and their statuses.
- As any user, I see only my assigned tasks.
- As Founder, I receive escalation alerts for overdue tasks automatically.

**Acceptance Criteria:**
- [ ] Task creation triggers WhatsApp + SMS within 2 minutes
- [ ] Daily digest runs at 9:00 AM via Celery scheduled job
- [ ] Overdue detection runs every hour via Celery beat
- [ ] No user can view another user's tasks (unless Founder or Management)

---

### 4.6 Founder Dashboard (Basic — Phase 1)

**Purpose:** Single-screen operational command centre for the Founder.

**KPIs displayed:**
- Total land files (by status)
- Court hearings today and next 7 days
- Overdue tasks count (by module)
- Advocate compliance status (Plans of Action pending)
- Documents pending / incomplete land files
- Recent activity feed (last 20 actions across the system)

**Travel Mode:**
- Toggle that reduces dashboard to critical alerts only
- Critical = overdue hearing compliance, overdue high-priority tasks, new legal orders uploaded

**Acceptance Criteria:**
- [ ] Dashboard loads in < 3 seconds
- [ ] All KPI cards link through to the relevant filtered list view
- [ ] Travel Mode correctly filters to critical alerts only
- [ ] Dashboard data refreshes every 5 minutes automatically

---

## 5. Phase 2 — Feature Requirements

### 5.1 Survey Management Module

**Survey Assignment:**
- Create survey task linked to land file
- Assign to in-house or freelance surveyor
- Set due date and priority

**Survey Data Fields:**
- Boundary match / mismatch (with notes)
- Encroachment — Yes/No; if yes: extent (acres/sq ft) and description
- Record extent vs ground extent (system flags discrepancy)
- Confidential surveyor notes (visible to in-house surveyors and Founder only)

**Uploads per survey:**
- Photos (multiple)
- Survey sketches (PDF/image)
- Drone videos
- FMB (Field Measurement Book) extracts

**Access Control:**
- Freelance surveyors: see only their assigned task — no other land files, no cross-visibility
- In-house surveyors: see all survey assignments
- Freelance token scoped to task ID

---

### 5.2 Revenue & Government Workflow Module

**Officer Mapping (per land file):**
- District Commissioner (DC)
- Assistant Commissioner (AC)
- Tahsildar
- Deputy Tahsildar
- Village Accountant (VA)
- Revenue Inspector (RI)
- ADLR / DDLR
- In-house Revenue Officer

**Workflows tracked:**
- Mutation
- Phodi
- Tippani
- RTC Correction
- Conversion

**Per workflow record:**
- Current status
- Date applied
- Officer handling
- Days pending (auto-calculated)
- Remarks / notes
- Document upload (application copy, order copy)

---

### 5.3 WhatsApp & SMS Automation

**Triggers:**
- Task assigned → immediate notification
- Hearing Plan of Action due in 3 days → reminder
- Hearing Plan of Action overdue → escalation
- Task overdue → escalation
- Daily digest → 9:00 AM summary
- Court order uploaded → notify in-house advocate supervisor

**Implementation:**
- Meta WhatsApp Business API (official only — no third-party)
- SMS via Twilio or MSG91 as fallback
- All notification events logged with delivery status
- Failed delivery retried after 15 minutes (max 3 retries)

---

### 5.4 Valuation & Market Intelligence

**Sub-Registrar Guidance Values (per land file):**
- Agricultural land — ₹ per acre
- Converted land — ₹ per acre
- Approved sites — ₹ per sq ft
- Last updated date

**Nearby Developments:**
- Project type — Plotted / Apartment / Villa / Farm Plot
- Developer name
- Distance from subject land (km)
- Project start year
- Selling price (₹ per unit)
- Available inventory

**Surrounding Infrastructure:**
- Category — IT/Software / College/School / Factory / Highway / Metro / Rail / Govt Project
- Name
- Distance (km)
- Notes

---

### 5.5 Advanced Dashboard (Phase 2)

**Additional KPIs:**
- Capital blocked vs productive (₹ Cr) — manually entered or computed from investment fields
- Land risk classification — High / Medium / Low (manually set by Founder)
- Revenue workflow SLA breaches
- Bottlenecks by officer name (days pending grouped by officer)
- Bottlenecks by advocate (overdue compliance grouped by advocate)
- Survey pending assignments

---

## 6. Phase 3 — Feature Requirements

### 6.1 Mobile Application
- iOS + Android
- React Native (shares API with web frontend)
- Roles: Founder (full dashboard), Field Staff (tasks only), Surveyors (survey tasks)
- Offline-capable task viewing for field staff

### 6.2 Post-Commitment Identity & Verification Module
- Enabled only after land file status = Committed (MOU/Agreement stage)
- Per seller and legal representative (LR):
  - Aadhaar upload — masked by default, unmasked only by Founder
  - PAN card
  - Family tree / genealogy documents
  - Legal heir certificates
  - Bank passbook / cancelled cheque
  - Photograph
- Strict encryption at rest (AES-256)
- Audit trail on every view of masked/unmasked Aadhaar

### 6.3 Investor & Capital Intelligence Module
- Investor database: category (Debt/Equity/JV), capacity (₹ min/max), risk appetite, credibility score
- Past and current investments linked to land files
- Per land proposal: suggested investors, suitability rating
- Strictly Founder-only access — no other role can view this module

### 6.4 Regulatory, Policy & News Intelligence
- Upload government circulars (BMRDA, BDA, BBMP, Revenue, State/Central)
- Tag circulars to specific land files or mark as general
- Area-specific news attachment to land files
- Daily consolidated founder briefing (auto-generated summary of activity)

### 6.5 Analytics & Reporting
- Land portfolio performance report
- Legal win/loss trend by advocate / court / case type
- Revenue workflow SLA report (average days pending by officer/workflow type)
- Task completion rate by user / module
- Document vault completeness report

---

## 7. Non-Functional Requirements

### 7.1 Performance
- API response time < 500ms for list endpoints (with pagination)
- Dashboard load time < 3 seconds
- File upload support up to 500MB per file (drone videos)
- Concurrent users: support 50 simultaneous users without degradation

### 7.2 Security
- All API endpoints require authentication (no public endpoints except login)
- RBAC enforced at API layer — never just frontend
- Sensitive columns encrypted at rest (Aadhaar, PAN, bank details, investor data)
- HTTPS enforced on all connections
- Rate limiting on login endpoint (5 attempts → 15 min lockout)
- AWS S3 files served via signed URLs only (never public URLs)
- No hard deletes anywhere in the system

### 7.3 Reliability
- 99.5% uptime target
- Daily automated database backups to S3 (or equivalent object store)
- Celery task queue with retry logic for notifications and for **Kafka** publishers
- **Apache Kafka** for ordered, replayable event streams (starting with audit fan-out)
- **Apache Cassandra** for durable, high-volume **audit log storage** fed from Kafka (operational analytics / retention); transactional `audit_log` in the primary DB remains authoritative for in-app queries

### 7.4 Auditability
- Every create, update, soft-delete action logged with: user ID, timestamp, old value, new value
- Login/logout events logged with IP
- Document view events logged
- Audit log is append-only — no modifications or deletions

### 7.5 Scalability
- Stateless Django backend — horizontally scalable behind a load balancer
- **CockroachDB** as the primary **self-hosted** OLTP store (distributed SQL, PostgreSQL protocol); optional read scaling via cluster topology / followers as the deployment matures
- **Kafka** + **Cassandra** for log/event scale-out without overloading the OLTP database
- S3-compatible private object storage for all binaries — no large uploads on app servers

---

## 8. Constraints & Assumptions

### Constraints
- WhatsApp integration must use official Meta Business API only — no third-party gateways
- No hard deletes anywhere in the system (legal/compliance requirement)
- External advocates must not be able to see any data outside their assigned cases — this is non-negotiable
- All file storage on AWS S3 — no local disk storage for uploads
- Cloud hosting costs, WhatsApp API charges, SMS charges, and domain costs are borne by the client

### Assumptions
- Client will obtain Meta WhatsApp Business API access independently (verification can take 2–4 weeks)
- Indian land hierarchy master data (Districts, Taluks, Hoblis, Villages of Karnataka) will be seeded into the database at project start
- Guidance values (Sub-Registrar rates) are manually entered by authorised users — no external API integration
- Phase 1 is web-only; mobile app is Phase 3

---

*Document Version: 1.0 | Last Updated: March 2026*

*Engineering tracking:* [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) (detail) · [COMPLETED.md](COMPLETED.md) (shipped) · [BACKLOG.md](BACKLOG.md) (not done, roles) · [COCKROACHDB_MIGRATIONS.md](COCKROACHDB_MIGRATIONS.md) (OLTP DDL review).
