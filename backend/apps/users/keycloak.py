"""
Keycloak OIDC authentication backend for DRF.

When ``KEYCLOAK_SERVER_URL`` is set (e.g. ``http://keycloak:8080``), this
backend validates Bearer JWTs issued by Keycloak, auto-provisions a Django
``User`` on first login, and maps Keycloak realm roles to ``UserRole``.

When ``KEYCLOAK_SERVER_URL`` is **empty** (the default), the backend is a
no-op — existing SimpleJWT auth handles everything.

Flow:
1. Fetch Keycloak realm's JWKS (public keys) from the well-known endpoint.
2. Decode and verify the Bearer token (RS256, audience, issuer).
3. Look up or create a Django User from the ``sub`` / ``email`` claims.
4. Map ``realm_access.roles`` → ``UserRole``.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import jwt as pyjwt
from django.conf import settings
from jwt import PyJWKClient
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from apps.users.models import User, UserRole

logger = logging.getLogger(__name__)

_KEYCLOAK_ROLE_MAP: dict[str, str] = {
    "limp_founder": UserRole.FOUNDER,
    "limp_management": UserRole.MANAGEMENT,
    "limp_inhouse_advocate": UserRole.IN_HOUSE_ADVOCATE,
    "limp_external_advocate": UserRole.EXTERNAL_ADVOCATE,
    "limp_revenue_team": UserRole.REVENUE_TEAM,
    "limp_surveyor_inhouse": UserRole.SURVEYOR_INHOUSE,
    "limp_surveyor_freelance": UserRole.SURVEYOR_FREELANCE,
    "limp_field_staff": UserRole.FIELD_STAFF,
}

_jwks_client: PyJWKClient | None = None
_jwks_fetched_at: float = 0
_JWKS_CACHE_SECONDS = 300


def _get_keycloak_config() -> dict[str, str]:
    server = getattr(settings, "KEYCLOAK_SERVER_URL", "")
    realm = getattr(settings, "KEYCLOAK_REALM", "limp")
    client_id = getattr(settings, "KEYCLOAK_CLIENT_ID", "limp-api")
    return {"server": server, "realm": realm, "client_id": client_id}


def _jwks_endpoint(cfg: dict[str, str]) -> str:
    return (
        f"{cfg['server'].rstrip('/')}/realms/{cfg['realm']}"
        f"/protocol/openid-connect/certs"
    )


def _issuer(cfg: dict[str, str]) -> str:
    return f"{cfg['server'].rstrip('/')}/realms/{cfg['realm']}"


def _get_jwks_client(cfg: dict[str, str]) -> PyJWKClient:
    global _jwks_client, _jwks_fetched_at  # noqa: PLW0603
    now = time.monotonic()
    if _jwks_client is None or (now - _jwks_fetched_at) > _JWKS_CACHE_SECONDS:
        _jwks_client = PyJWKClient(_jwks_endpoint(cfg), cache_keys=True)
        _jwks_fetched_at = now
    return _jwks_client


def _map_role(realm_roles: list[str]) -> str:
    """Return the highest-privilege LIMP role found in Keycloak realm roles."""
    for kc_role, django_role in _KEYCLOAK_ROLE_MAP.items():
        if kc_role in realm_roles:
            return django_role
    return UserRole.FIELD_STAFF


def _decode_keycloak_token(token: str) -> dict[str, Any]:
    cfg = _get_keycloak_config()
    if not cfg["server"]:
        raise AuthenticationFailed("Keycloak not configured")

    try:
        client = _get_jwks_client(cfg)
        signing_key = client.get_signing_key_from_jwt(token)
        payload: dict[str, Any] = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=cfg["client_id"],
            issuer=_issuer(cfg),
            options={
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )
    except pyjwt.ExpiredSignatureError as exc:
        raise AuthenticationFailed("Keycloak token expired") from exc
    except pyjwt.InvalidTokenError as exc:
        raise AuthenticationFailed(f"Invalid Keycloak token: {exc}") from exc

    return payload


def _get_or_create_user(payload: dict[str, Any]) -> User:
    email = payload.get("email", "")
    if not email:
        raise AuthenticationFailed("Keycloak token missing email claim")

    realm_roles: list[str] = payload.get("realm_access", {}).get("roles", [])
    role = _map_role(realm_roles)

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "first_name": payload.get("given_name", ""),
            "last_name": payload.get("family_name", ""),
            "role": role,
            "is_active": True,
        },
    )
    if not created:
        changed = False
        if user.role != role:
            user.role = role
            changed = True
        for attr, claim in [
            ("first_name", "given_name"),
            ("last_name", "family_name"),
        ]:
            val = payload.get(claim, "")
            if val and getattr(user, attr) != val:
                setattr(user, attr, val)
                changed = True
        if changed:
            user.save()
    else:
        logger.info("Auto-provisioned Keycloak user %s with role %s", email, role)

    return user


class KeycloakJWTAuthentication(BaseAuthentication):
    """
    DRF authentication backend that validates Keycloak-issued JWTs.

    Added **alongside** ``JWTAuthentication`` so both SimpleJWT (direct
    login) and Keycloak tokens are accepted.  When ``KEYCLOAK_SERVER_URL``
    is empty the backend returns ``None`` (skip) for every request.
    """

    def authenticate(self, request: Request):
        cfg = _get_keycloak_config()
        if not cfg["server"]:
            return None

        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None

        token = header[7:]

        try:
            payload = _decode_keycloak_token(token)
        except AuthenticationFailed:
            return None

        user = _get_or_create_user(payload)
        return (user, payload)

    def authenticate_header(self, request: Request) -> str:
        return 'Bearer realm="keycloak"'
