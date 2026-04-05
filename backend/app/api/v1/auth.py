"""OAuth authentication routes — Google and GitHub login with JWT issuance."""
from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.db import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30


def _create_jwt(user_id: str, email: str) -> str:
    """Create a signed JWT for authenticated user."""
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


async def _upsert_user(
    session: AsyncSession,
    email: str,
    name: str | None,
    avatar_url: str | None,
    provider: str,
    provider_id: str,
) -> User:
    """Create or update user, return the user object."""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            name=name,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
        )
        session.add(user)
    else:
        user.name = name or user.name
        user.avatar_url = avatar_url or user.avatar_url
        user.last_login_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(user)
    return user


def _set_auth_cookie(response: RedirectResponse, token: str) -> None:
    """Set JWT as httpOnly cookie."""
    response.set_cookie(
        key="cb_token",
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=JWT_EXPIRY_DAYS * 86400,
        path="/",
    )


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------

@router.get("/google")
async def google_login():
    """Redirect to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": _google_callback_url(),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


@router.get("/google/callback")
async def google_callback(
    code: str | None = None,
    error: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback — exchange code for user info, issue JWT."""
    if error or not code:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=google_denied")

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": _google_callback_url(),
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            logger.error("Google token exchange failed: %s", token_resp.text)
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=google_token_failed")

        tokens = token_resp.json()
        access_token = tokens["access_token"]

        # Fetch user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=google_userinfo_failed")

        info = user_resp.json()

    user = await _upsert_user(
        session,
        email=info["email"],
        name=info.get("name"),
        avatar_url=info.get("picture"),
        provider="google",
        provider_id=str(info["id"]),
    )

    token = _create_jwt(str(user.id), user.email)
    # Redirect to frontend callback route which sets the cookie on the frontend domain
    return RedirectResponse(f"{settings.FRONTEND_URL}/api/auth/callback?token={token}")


def _google_callback_url() -> str:
    """Build the Google OAuth callback URL."""
    return f"{settings.FRONTEND_URL.rstrip('/')}/api/backend/v1/auth/google/callback" if not settings.is_production else "https://contextbharat-api-507218003648.asia-south1.run.app/v1/auth/google/callback"


# ---------------------------------------------------------------------------
# GitHub OAuth
# ---------------------------------------------------------------------------

@router.get("/github")
async def github_login():
    """Redirect to GitHub OAuth authorization."""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")

    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": _github_callback_url(),
        "scope": "read:user user:email",
        "state": state,
    }
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{urlencode(params)}")


@router.get("/github/callback")
async def github_callback(
    code: str | None = None,
    error: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback — exchange code for user info, issue JWT."""
    if error or not code:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=github_denied")

    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": _github_callback_url(),
            },
            headers={"Accept": "application/json"},
        )
        if token_resp.status_code != 200:
            logger.error("GitHub token exchange failed: %s", token_resp.text)
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=github_token_failed")

        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        if not access_token:
            logger.error("GitHub token response missing access_token: %s", tokens)
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=github_token_failed")

        # Fetch user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        info = user_resp.json()

        # Fetch email (may be private)
        email = info.get("email")
        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            )
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else emails[0]["email"]

    user = await _upsert_user(
        session,
        email=email,
        name=info.get("name") or info.get("login"),
        avatar_url=info.get("avatar_url"),
        provider="github",
        provider_id=str(info["id"]),
    )

    token = _create_jwt(str(user.id), user.email)
    return RedirectResponse(f"{settings.FRONTEND_URL}/api/auth/callback?token={token}")


def _github_callback_url() -> str:
    """Build the GitHub OAuth callback URL."""
    return f"{settings.FRONTEND_URL.rstrip('/')}/api/backend/v1/auth/github/callback" if not settings.is_production else "https://contextbharat-api-507218003648.asia-south1.run.app/v1/auth/github/callback"


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

@router.get("/me")
async def get_me(request: Request, session: AsyncSession = Depends(get_db)):
    """Return current user info from JWT cookie or Bearer header."""
    token = None
    # Check Authorization header first (from frontend proxy)
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    # Fall back to cookie (direct browser access)
    if not token:
        token = request.cookies.get("cb_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid token: malformed user ID")

    result = await session.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "provider": user.provider,
    }


@router.get("/logout")
async def logout():
    """Clear the auth cookie."""
    response = RedirectResponse(f"{settings.FRONTEND_URL}/login", status_code=302)
    response.delete_cookie("cb_token", path="/")
    return response
