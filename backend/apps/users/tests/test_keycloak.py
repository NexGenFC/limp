"""
Tests for Keycloak JWT authentication backend.

These tests mock the JWKS fetch and token decode so they run without a
real Keycloak instance (CI-safe).
"""

from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIRequestFactory

from apps.users.keycloak import KeycloakJWTAuthentication, _map_role
from apps.users.models import User, UserRole

factory = APIRequestFactory()

KEYCLOAK_SETTINGS = {
    "KEYCLOAK_SERVER_URL": "http://keycloak:8180",
    "KEYCLOAK_REALM": "limp",
    "KEYCLOAK_CLIENT_ID": "limp-api",
}


def test_map_role_founder():
    assert _map_role(["limp_founder", "default-roles-limp"]) == UserRole.FOUNDER


def test_map_role_external_advocate():
    assert (
        _map_role(["limp_external_advocate", "offline_access"])
        == UserRole.EXTERNAL_ADVOCATE
    )


def test_map_role_fallback():
    assert _map_role(["some_other_role"]) == UserRole.FIELD_STAFF


def test_backend_returns_none_when_keycloak_unconfigured():
    auth = KeycloakJWTAuthentication()
    request = factory.get("/", HTTP_AUTHORIZATION="Bearer fake.jwt.here")
    assert auth.authenticate(request) is None


@override_settings(**KEYCLOAK_SETTINGS)
@pytest.mark.django_db
def test_backend_provisions_user_on_valid_token():
    payload = {
        "sub": "kc-uuid-1234",
        "email": "newuser@keycloak.test",
        "given_name": "New",
        "family_name": "User",
        "realm_access": {"roles": ["limp_management"]},
    }

    with patch("apps.users.keycloak._decode_keycloak_token", return_value=payload):
        auth = KeycloakJWTAuthentication()
        request = factory.get("/", HTTP_AUTHORIZATION="Bearer valid.keycloak.jwt")
        result = auth.authenticate(request)

    assert result is not None
    user, claims = result
    assert isinstance(user, User)
    assert user.email == "newuser@keycloak.test"
    assert user.role == UserRole.MANAGEMENT
    assert user.first_name == "New"
    assert claims["sub"] == "kc-uuid-1234"


@override_settings(**KEYCLOAK_SETTINGS)
@pytest.mark.django_db
def test_backend_updates_existing_user_role():
    User.objects.create_user(
        email="existing@keycloak.test",
        password="pw12345678",
        role=UserRole.FIELD_STAFF,
    )
    payload = {
        "sub": "kc-uuid-9999",
        "email": "existing@keycloak.test",
        "given_name": "Exists",
        "family_name": "Already",
        "realm_access": {"roles": ["limp_founder"]},
    }

    with patch("apps.users.keycloak._decode_keycloak_token", return_value=payload):
        auth = KeycloakJWTAuthentication()
        request = factory.get("/", HTTP_AUTHORIZATION="Bearer valid.keycloak.jwt")
        user, _ = auth.authenticate(request)

    assert user.role == UserRole.FOUNDER
    assert user.first_name == "Exists"
