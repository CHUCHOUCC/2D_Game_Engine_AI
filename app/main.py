from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response

from .agent import AgentError, GameAgent
from .cache import cached_generation
from .hardening import HardeningMiddleware, check_configuration, is_production
from .learning_api import router as learning_router
from .providers import AiProviderError, create_provider
from .schemas import GenerateRequest, scene_dicts
from .security import require_service_token

load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Refuses to start in production with a weak or example service key.
    check_configuration()
    yield


# No CORS middleware on purpose: browsers must not call this service.
# Only the backend (which signs service tokens) does.
app = FastAPI(
    title="2D Engine AI Service",
    version="2.1.0",
    lifespan=lifespan,
    docs_url=None if is_production() else "/docs",
    redoc_url=None,
    openapi_url=None if is_production() else "/openapi.json",
)
app.add_middleware(HardeningMiddleware)
app.include_router(learning_router)


def get_agent() -> GameAgent:
    try:
        return GameAgent(create_provider())
    except AiProviderError as error:
        raise HTTPException(status_code=503, detail=str(error))


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate", dependencies=[Depends(require_service_token)])
def generate(body: GenerateRequest, response: Response, agent: GameAgent = Depends(get_agent)):
    scene = scene_dicts(body.scene)
    try:
        objects, hit = cached_generation(agent.provider, body.prompt, scene, lambda: agent.generate(body.prompt, scene))
        # Lets the backend (and the logs) see whether the external AI API was called.
        response.headers["X-Cache"] = "HIT" if hit else "MISS"
        return {"objects": objects}
    except AgentError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except AiProviderError as error:
        raise HTTPException(status_code=502, detail=str(error))
