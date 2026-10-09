import os
import threading
import time

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

EXPECTED_ISSUER = "2d-engine-backend"
AUDIENCE = "ai-service"
MIN_KEY_LENGTH = 32
# Tokens are valid for 60 s; a little leeway covers clock differences.
LEEWAY_SECONDS = 5

_bearer = HTTPBearer(auto_error=False)



class ReplayCache:
    """Remembers token ids (jti) until they expire, so a captured token cannot
    be sent twice. In memory: enough for one instance of the service."""

    def __init__(self):
        self._seen = {}
        self._lock = threading.Lock()

    def first_use(self, jti: str, expires_at: float) -> bool:
        now = time.time()
        with self._lock:
            for old in [k for k, exp in self._seen.items() if exp < now]:
                del self._seen[old]
            if jti in self._seen:
                return False
            self._seen[jti] = expires_at
            return True


replay_cache = ReplayCache()



def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def require_service_token(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    """Only the backend can sign tokens with AI_SERVICE_KEY, so only it can call this service."""
    key = os.environ.get("AI_SERVICE_KEY", "")
    if len(key) < MIN_KEY_LENGTH:
        raise HTTPException(status_code=503, detail="Service key is not configured")
    if credentials is None:
        raise _unauthorized("Missing service token")
    try:
        claims = jwt.decode(
            credentials.credentials,
            key,
            algorithms=["HS256"],
            audience=AUDIENCE,
            issuer=EXPECTED_ISSUER,
            leeway=LEEWAY_SECONDS,
            options={"require": ["exp", "iat", "jti", "aud", "iss"]},
        )
    except jwt.PyJWTError:
        raise _unauthorized("Invalid service token")
    if not replay_cache.first_use(claims["jti"], claims["exp"] + LEEWAY_SECONDS):
        raise _unauthorized("Service token already used")
    return claims
