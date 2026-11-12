from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response

from .agent import AgentError, GameAgent
from .cache import cached_generation
from .edits import parse_edit, removed_ids
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
def generate(body: GenerateRequest, response: Response):
    """Apply a natural-language request to the scene: what it removes and what it adds.

    Removals ("borra los enemigos", "elimina todo") are decided by app/edits.py without calling
    the model; anything the request also asks to add goes to the model, on the scene without the
    removed objects. A request that only removes never touches the external API.
    """
    scene = scene_dicts(body.scene)
    edit = parse_edit(body.prompt)
    removed = removed_ids(scene, edit.remove_kinds)
    gone = set(removed)
    remaining = [obj for obj in scene if obj["id"] not in gone]
    objects, hit = [], True
    if edit.add_request:
        # Resolved only when needed (a request that only removes works even without a provider);
        # tests replace it through dependency_overrides as with any dependency.
        agent = app.dependency_overrides.get(get_agent, get_agent)()
        try:
            objects, hit = cached_generation(
                agent.provider, edit.add_request, remaining, lambda: agent.generate(edit.add_request, remaining)
            )
        except AgentError as error:
            raise HTTPException(status_code=502, detail=str(error))
        except AiProviderError as error:
            raise HTTPException(status_code=502, detail=str(error))
    # Lets the backend (and the logs) see whether the external AI API was called.
    response.headers["X-Cache"] = "HIT" if hit else "MISS"
    return {"objects": objects, "removed": removed}
