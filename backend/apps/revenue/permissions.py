from rest_framework import permissions
from apps.users.models import UserRole  # Fix 5: Use Enum


class IsRevenueTeamOrManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Explicit role check using Enums
        allowed_roles = {UserRole.FOUNDER, UserRole.MANAGEMENT, UserRole.REVENUE_TEAM}
        return request.user.role in allowed_roles
