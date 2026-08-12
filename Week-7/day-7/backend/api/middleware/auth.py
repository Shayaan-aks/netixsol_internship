"""
JWT + API Key authentication middleware.
Supports both Bearer token and X-API-Key header authentication.
"""
import time
import hashlib
from typing import Optional
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import jwt

from backend.config.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _hash_key(key: str) -> str:
    """Hash an API key for constant-time comparison."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validate X-API-Key header against configured keys."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    valid_hashes = {_hash_key(k) for k in settings.api_keys_list}
    if _hash_key(api_key) not in valid_hashes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return api_key


def create_jwt_token(subject: str, extra_claims: dict = None) -> str:
    """Create a short-lived JWT for session-based auth."""
    payload = {
        "sub": subject,
        "iat": int(time.time()),
        "exp": int(time.time()) + (settings.jwt_expiry_minutes * 60),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_jwt_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> dict:
    """Validate Bearer JWT token and return its claims."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )


# Flexible dependency — accepts either API key OR JWT
async def require_auth(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> dict:
    """Accept either a valid API key or a valid JWT Bearer token."""
    if api_key and api_key in settings.api_keys_list:
        return {"auth_type": "api_key", "subject": "api_client"}
    if credentials:
        try:
            return verify_jwt_token(credentials)
        except HTTPException:
            pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid authentication required (API key or Bearer token).",
    )
