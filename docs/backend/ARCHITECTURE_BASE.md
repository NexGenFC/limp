# Backend domain base (Phase 1 scaffold)

**Purpose:** Single map of the **land-anchored** domain apps so implementers share the same mental model. Product detail remains in PRD / HLD; this doc matches **what is in the repo today**.

**Assignee briefs:** each of [`ASSIGNMENT_PERSON_01_LEGAL.md`](ASSIGNMENT_PERSON_01_LEGAL.md) … [`ASSIGNMENT_PERSON_04_DOCUMENTS_STORAGE.md`](ASSIGNMENT_PERSON_04_DOCUMENTS_STORAGE.md) starts with **§0 Start here** (full reading list, `uv sync` + `migrate`, integration map, code pointers).

**Rule:** Every new domain row links to `land.LandFile` via FK name **`land`** (see [`docs/rules.md`](../rules.md)). Soft delete + audit use `apps.core.models.BaseModel`. Domain model PKs are **UUIDv7** (time-ordered, globally unique).

**Auth:** SimpleJWT (direct login) + optional **Keycloak OIDC** (`apps/users/keycloak.py`); both run simultaneously. When Keycloak is disabled (default in dev/CI), only SimpleJWT is used.

**Local DB:** If `migrate` fails after `git pull`, reset SQLite — see **[`docs/DEV_DATABASE.md`](../DEV_DATABASE.md)** (why and exact commands).

---

## Layout

| Django app | Label | Role |
|------------|-------|------|
| `apps.land` | `land` | Master file (`LandFile`, geography FK) — **anchor** |
| `apps.legal` | `legal` | Litigation cases (`LegalCase` → expand) |
| `apps.revenue` | `revenue` | Government / revenue workflows (`GovernmentWorkflow`) |
| `apps.tasks` | `tasks` | Operational tasks + `NotificationLog` |
| `apps.documents` | `documents` | Checklist rows + S3-backed `DocumentVersion` |

API wiring: [`backend/config/api_v1_urls.py`](../../backend/config/api_v1_urls.py) includes each app’s `urls.py` (routers added as features ship).

---

## Reverse relations from `LandFile`

Use these `related_name`s when navigating from a land file in shell or serializers:

| Related model | `related_name` on `LandFile` |
|---------------|------------------------------|
| `LegalCase` | `legal_cases` |
| `GovernmentWorkflow` | `government_workflows` |
| `Task` | `tasks` |
| `LandDocumentChecklistItem` | `document_checklist_items` |

---

## Constraints (intentional)

- **`GovernmentWorkflow`:** at most one **active** (`is_deleted=False`) row per `(land, kind)` — see `UniqueConstraint` in `revenue/models.py`.
- **`LandDocumentChecklistItem`:** at most one **active** row per `(land, document_kind)` — see `documents/models.py`.

If the business needs multiple active rows of the same kind (e.g. two parallel mutations), relax or replace these constraints in a **new migration** after product sign-off.

---

## What implementers add next

- **Serializers, ViewSets, permissions** in each app (see per-person `ASSIGNMENT_*.md`).
- **New migrations only** for schema changes — do not rewrite `0001_initial` after merge to `main`.
- **S3 / WhatsApp:** follow HLD; no binary uploads through Django ([`docs/rules.md`](../rules.md)).

---

*April 2026 — aligned with `0001_initial` for legal, revenue, tasks, documents.*
