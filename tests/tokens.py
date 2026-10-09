import time
import uuid

import jwt

KEY = "test-service-key-that-has-32-chars!!"


def service_token(key=KEY, audience="ai-service", issuer="2d-engine-backend", lifetime=60, jti=None):
    now = int(time.time())
    payload = {"iss": issuer, "aud": audience, "sub": "backend", "scope": "ai",
               "jti": jti or uuid.uuid4().hex, "iat": now, "exp": now + lifetime}
    return jwt.encode(payload, key, algorithm="HS256")


def auth(**kwargs):
    return {"Authorization": f"Bearer {service_token(**kwargs)}"}
