"""
Role-based permission classes for LIMP.

Usage: combine with DRF's ``permission_classes`` on ViewSets / views.
Geography endpoints use ``IsAuthenticated`` (all roles may read reference data).
Domain endpoints (land, legal, …) use the role-specific classes below.

See PRD §3.2 Access Matrix for the authoritative role × module table.
"""

from rest_framework.permissions import BasePermission

from apps.users.models import UserRole

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LAND_FULL = frozenset({UserRole.FOUNDER, UserRole.MANAGEMENT})
_LAND_READ = frozenset(
    {
        UserRole.FOUNDER,
        UserRole.MANAGEMENT,
        UserRole.IN_HOUSE_ADVOCATE,
        UserRole.REVENUE_TEAM,
        UserRole.SURVEYOR_INHOUSE,
    }
)

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


# ---------------------------------------------------------------------------
# Reusable role guards
# ---------------------------------------------------------------------------


class IsFounder(BasePermission):
    """Only FOUNDER role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.FOUNDER
        )


class IsFounderOrManagement(BasePermission):
    """FOUNDER or MANAGEMENT."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in _LAND_FULL
        )


# ---------------------------------------------------------------------------
# Land Master permissions (PRD §3.2)
# ---------------------------------------------------------------------------


class LandPermission(BasePermission):
    """
    Land Master access:

    * Full CRUD — FOUNDER, MANAGEMENT
    * Read-only — IN_HOUSE_ADVOCATE, REVENUE_TEAM, SURVEYOR_INHOUSE
    * No access  — EXTERNAL_ADVOCATE (needs case scoping, not yet wired),
                   SURVEYOR_FREELANCE, FIELD_STAFF
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return user.role in _LAND_READ

        return user.role in _LAND_FULL


# ---------------------------------------------------------------------------
# Document permissions (PRD §7)
# ---------------------------------------------------------------------------


class DocumentPermission(BasePermission):
    """
    Document vault access:

    * Full access (upload, download, manage) — FOUNDER, MANAGEMENT
    * Read-only — IN_HOUSE_ADVOCATE, REVENUE_TEAM, SURVEYOR_INHOUSE
    * No access — EXTERNAL_ADVOCATE, SURVEYOR_FREELANCE, FIELD_STAFF
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return user.role in _LAND_READ

        return user.role in _LAND_FULL


class DocumentDownloadPermission(BasePermission):
    """
    Allows read-roles to make POST requests ONLY for generation of Presigned Download URLs.
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        return user.role in _LAND_READ


class IdentityDocumentPermission(BasePermission):
    """
    Identity/KYC document access - strictly restricted to FOUNDER and MANAGEMENT only.
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        return user.role in _LAND_FULL
