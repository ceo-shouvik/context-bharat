"""
Security headers and rate limiting middleware for the Context Bharat API.
"""
from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limit configuration
# ---------------------------------------------------------------------------
# path prefix -> (max_requests, window_seconds)
_RATE_LIMIT_RULES: list[tuple[str, int, int]] = [
    ("/v1/docs/query", 10, 60),   # expensive query endpoint
]
_DEFAULT_RATE_LIMIT = 100   # requests
_DEFAULT_RATE_WINDOW = 60   # seconds


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting common proxy headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def _match_rate_limit(path: str) -> tuple[int, int]:
    """Return (max_requests, window_seconds) for the given path."""
    for prefix, limit, window in _RATE_LIMIT_RULES:
        if path.startswith(prefix):
            return limit, window
    return _DEFAULT_RATE_LIMIT, _DEFAULT_RATE_WINDOW


# ---------------------------------------------------------------------------
# Rate Limiting Middleware
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP rate limiting backed by Redis INCR + TTL.

    * 100 req/min default for public endpoints
    * 10 req/min for /v1/docs/query (expensive)
    * Skips /health
    * Degrades gracefully (allows request) when Redis is unavailable
    """

    _SKIP_PATHS = {"/health"}

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip health endpoint
        if path in self._SKIP_PATHS:
            return await call_next(request)

        client_ip = _get_client_ip(request)
        max_requests, window = _match_rate_limit(path)

        # Build a Redis key that encodes IP + window bucket
        bucket = int(time.time()) // window
        redis_key = f"rl:{client_ip}:{path}:{bucket}"

        current_count = 0
        allowed = True
        ttl_remaining = window  # default if Redis is unavailable

        try:
            from app.core.redis_client import _get_client

            client = _get_client()
            if client is not None:
                # INCR is atomic; first call auto-creates key with value 1
                current_count = client.incr(redis_key)
                if current_count == 1:
                    # First request in this bucket — set the TTL
                    client.expire(redis_key, window)

                # Compute the remaining TTL for headers
                raw_ttl = client.ttl(redis_key)
                if raw_ttl and raw_ttl > 0:
                    ttl_remaining = raw_ttl

                if current_count > max_requests:
                    allowed = False
        except Exception as exc:
            # Redis down — degrade open (allow request)
            logger.debug("Rate limiter Redis error, allowing request: %s", exc)

        remaining = max(0, max_requests - current_count)
        reset_timestamp = int(time.time()) + ttl_remaining

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please retry after the indicated time.",
                    }
                },
                headers={
                    "Retry-After": str(ttl_remaining),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_timestamp),
                },
            )

        # Proceed with the request, then attach rate-limit headers
        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_timestamp)
        return response


# ---------------------------------------------------------------------------
# Security Headers Middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to every response."""

    _HEADERS = {
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        for header, value in self._HEADERS.items():
            response.headers[header] = value
        return response
