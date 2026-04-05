# Document Tests

This directory contains tests for the document vault functionality.

## Test Files

- `test_models.py` - Tests for DocumentVersion and LandDocumentChecklistItem models
- `test_services.py` - Tests for S3 presigned URL service functions and completion stats
- `test_serializers.py` - Tests for IdentityDocumentSerializer masking logic
- `test_kyc.py` - Verification tests: masked ID numbers in API response, completion_percentage formula in LandFileSerializer
- `test_views.py` - Tests for API views with RBAC and S3 configuration handling

## Running Tests

```bash
cd backend
python -m pytest apps/documents/tests/ -v
```

## Test Coverage

### Models
- DocumentVersion and LandDocumentChecklistItem creation and relationships

### S3 Services
- Presigned upload/download URL generation
- Object existence checks
- S3 not configured handling (returns 503)

### Completion Stats
- calculate_land_completion with no items (returns 0.0)
- calculate_land_completion land not found (raises ValueError)
- get_overall_completion_stats with no lands (returns 0.0)

### Serializers
- mask_aadhaar: 1234-5678-9012 → XXXX-XXXX-9012
- mask_pan: ABCDE1234F → XXXXX1234X
- mask_document_number dispatches based on document type

### RBAC
- IdentityDocument: FOUNDER, MANAGEMENT only (others get 403)
- Document vault: FIELD_STAFF forbidden (403)
- Read-only roles (IN_HOUSE_ADVOCATE) cannot write

### Views
- IdentityDocumentViewSet CRUD operations
- LandCompletionStatsView: per-land and overall stats