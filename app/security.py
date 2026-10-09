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
