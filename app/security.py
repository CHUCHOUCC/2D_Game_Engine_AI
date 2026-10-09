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
