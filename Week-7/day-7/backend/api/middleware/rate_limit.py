"""
Rate Limiting Middleware — Sliding Window Algorithm
Uses in-memory store (replace with Redis for multi-worker deployments).
"""
import time
import asyncio
from collections import defaultdict, deque
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter.
    In production with multiple workers, replace _windows with Redis ZADD/ZCOUNT.
    """

    EXEMPT_PATHS = {"/v1/health", "/v1/ready", "/v1/live", "/metrics", "/"}

    def __init__(self, app, requests_per_minute: int = 60, burst_size: int = 10):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.burst = burst_size
        self._windows: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _get_client_id(self, request: Request) -> str:
        """Use API key if present, else fall back to IP."""
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"key:{api_key[:8]}"
        forwarded = request.headers.get("X-Forwarded-For", "")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
        return f"ip:{ip}"

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_id = self._get_client_id(request)
        now = time.time()
        window_start = now - 60.0  # 60-second window

        async with self._lock:
            window = self._windows[client_id]
            # Remove timestamps outside window
            while window and window[0] < window_start:
                window.popleft()

            if len(window) >= self.rpm:
                retry_after = int(60 - (now - window[0])) + 1
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": f"Too many requests. Limit: {self.rpm}/minute.",
                        "retry_after_seconds": retry_after,
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.rpm),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(now + retry_after)),
                    },
                )

            window.append(now)
            remaining = self.rpm - len(window)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rpm)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        return response
