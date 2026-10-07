import hmac
import os

from fastapi import Header, HTTPException


def require_service_key(x_service_key: str = Header(default="")):
    """Only the backend knows AI_SERVICE_KEY, so only it can call this service."""
    expected = os.environ.get("AI_SERVICE_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Service key is not configured")
    if not hmac.compare_digest(x_service_key.encode("utf-8"), expected.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid service key")
