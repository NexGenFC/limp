# Backend assignment — Person 4: Documents, S3 & KYC (Part 2)

**Owner:** Person 4 (Documents / storage / security)  
**Repo:** LIMP monorepo — work only under `backend/` for this brief.  
**Product context:** Client §7 (Docs), §6.2 (KYC), HLD §3.3 upload flow.

**Core App:** `apps.documents`  
**Security Focus:** Identity Masking & Row-Level PERIMETER.

---

## 0. Start here (fully self-contained)

### 0.1 Repo layout

| Area | Path | Your touch |
|------|------|------------|
| Your app | `backend/apps/documents/` | **Primary** — views, serializers, models, tests |
| Services | `backend/apps/documents/services.py` | Implementation of analytics & S3 hooks |
| Serializers | `backend/apps/documents/serializers.py` | Add masking logic |

### 0.2 Machine setup (New Session)

```bash
# From repo root
git checkout main && git pull --rebase origin main
cd backend && uv sync --all-groups && uv run python manage.py migrate
uv run python manage.py runserver 0.0.0.0:8000
```

---

## 1. Relevant Schema Reference

### 1.1 `apps.documents.models.DocumentVersion` (Existing)
- `s3_key`, `original_filename`, `version_number`.
- `checklist_item` (FK to `LandDocumentChecklistItem`).

### 1.2 `apps.documents.models.IdentityDocument` (NEW)
- `land`: FK to `LandFile`.
- `document_type`: Choices (AADHAAR, PAN, PASSPORT).
- `id_number`: Encrypted-ready string (use `CharField` for now).
- `s3_key`: String (Path to file in S3).

---

## 2. Your Scope — Current Status

### ✅ Phase 1 Part 1 — COMPLETED
- S3 Presigned URL services (Upload, Download, Confirm) are live.
- Document checklist model & versioning logic are live.
- Row-level RBAC is enforced (Users only see docs for assigned tasks).

### 🚀 Phase 1 Part 2 — Identity/KYC & Document Intelligence — NEW
**Goal:** Handle sensitive identify documents and provide completion transparency.

#### 2.1 Identity/KYC Module (PRD §6.2)
- **Model:** Create `IdentityDocument` as defined in 1.2.
- **Masking:** Implement logic in `IdentityDocumentSerializer` (either `to_representation` or `SerializerMethodField`).
  - **Aadhaar:** `1234-5678-9012` → `XXXX-XXXX-9012` (Mask first 8 digits).
  - **PAN:** `ABCDE1234F` → `XXXXX1234X` (Mask first 5 and last 1 characters).
- **RBAC:** Strictly restricted to `UserRole.FOUNDER` and `UserRole.MANAGEMENT`.

#### 2.2 Document Completion Analytics
- **Logic:** Create a service method `calculate_land_completion(land_id)` in `services.py`.
  - **Formula:** `(Count of item where checklist_status='CERTIFIED_OBTAINED') / (Total items where checklist_status != 'NOT_APPLICABLE')`.
  - Return as a **float** (0.0 to 1.0).
- **Public Hook:** Expose a method `get_overall_completion_stats()` that returns the average across all lands (to be consumed by Person 3's Dashboard).

---

## 3. Coordination & Conflicts

- **Coordination:** You MUST provide the `get_overall_completion_stats()` service. Person 3 is waiting to import this for the Founder Dashboard stats.
- **Security:** Do not log unmasked Aadhaar/PAN numbers in any `print` or `logger` statements.

---

## 4. Verification

1. **Unit Test:** `apps/documents/tests/test_kyc.py`
   - Assert `id_number` is masked in the API response.
   - Assert `completion_percentage` in `LandFileSerializer` matches the formula.
2. **Commands:**
   ```bash
   cd backend && uv run pytest apps/documents/
   ```

---

*Brief version: April 2026 — Part 2 Update.*
