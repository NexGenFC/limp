"""
API v1 URL includes.

All routes under /api/v1/ are composed here so feature teams can add a single
``include()`` line without editing the root ``config/urls.py`` (reduces merge
conflicts). Keep includes ordered alphabetically by app label unless a
dependency requires otherwise.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.documents.urls")),
    path("", include("apps.geography.urls")),
    path("", include("apps.land.urls")),
    path("", include("apps.legal.urls")),
    path("", include("apps.revenue.urls")),
    path("", include("apps.tasks.urls")),
    path("", include("apps.users.urls")),
]
