from rest_framework import permissions


class IsRevenueTeamOrManagement(permissions.BasePermission):
    """
    Strict RBAC for the Revenue Module (§3.3).
    Only allows access to Founders, Management, and Revenue Team members.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # These strings must match the UserRole choices in apps.users.models
        allowed_roles = {"FOUNDER", "MANAGEMENT", "REVENUE_TEAM"}

        user_role = getattr(request.user, "role", None)
        return user_role in allowed_roles
