# Document Tests

This directory contains tests for the document vault functionality.

## Test Files

- `test_models.py` - Tests for DocumentVersion and LandDocumentChecklistItem models
- `test_services.py` - Tests for S3 presigned URL service functions
- `test_views.py` - Tests for API views with RBAC and S3 configuration handling

## Running Tests

```bash
cd backend
python -m pytest apps/documents/tests/ -v
```

## Test Coverage

- Model creation and relationships
- S3 service functions (presigned upload/download URLs, object existence checks)
- S3 not configured handling (returns 503)
- RBAC: forbidden roles (FIELD_STAFF) get 403
- RBAC: read-only roles (IN_HOUSE_ADVOCATE) cannot write