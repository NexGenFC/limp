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


_LEGAL_VIEW = frozenset(
    {
        UserRole.FOUNDER,
        UserRole.MANAGEMENT,
        UserRole.IN_HOUSE_ADVOCATE,
        UserRole.EXTERNAL_ADVOCATE,
    }
)

_IN_HOUSE_OR_ABOVE = frozenset(
    {
        UserRole.FOUNDER,
        UserRole.MANAGEMENT,
        UserRole.IN_HOUSE_ADVOCATE,
    }
)


class CanViewLegalCases(BasePermission):
    """List / retrieve legal cases (includes EXTERNAL_ADVOCATE; scope in queryset)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role in _LEGAL_VIEW
        )


class IsInHouseAdvocateOrAbove(BasePermission):
    """FOUNDER, MANAGEMENT, or IN_HOUSE_ADVOCATE (not external)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role in _IN_HOUSE_OR_ABOVE
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
