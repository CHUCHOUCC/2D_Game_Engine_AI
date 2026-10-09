from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException

from .agent import AgentError, GameAgent
from .learning_api import router as learning_router
from .providers import AiProviderError, create_provider
from .schemas import GenerateRequest, scene_dicts
from .security import require_service_token

load_dotenv()

# No CORS middleware on purpose: browsers must not call this service.
# Only the backend (which signs service tokens) does.
app = FastAPI(title="2D Engine AI Service", version="2.0.0")
app.include_router(learning_router)
