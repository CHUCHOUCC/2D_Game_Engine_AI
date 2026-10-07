from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agent import AgentError, GameAgent
from .providers import AiProviderError, create_provider
from .security import require_service_key

load_dotenv()

# No CORS middleware on purpose: browsers must not call this service.
# Only the backend (which holds the service key) does.
app = FastAPI(title="2D Engine AI Service")


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)


def get_agent() -> GameAgent:
    return GameAgent(create_provider())


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate", dependencies=[Depends(require_service_key)])
def generate(body: GenerateRequest, agent: GameAgent = Depends(get_agent)):
    try:
        return {"objects": agent.generate(body.prompt)}
    except AgentError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except AiProviderError as error:
        raise HTTPException(status_code=502, detail=str(error))
