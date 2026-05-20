"""Agent Service — FastAPI application entry point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from pydantic import BaseModel

from shared.models import RoleAttributes, ResponseStyle
from src.config import settings
from src.persona.registry import PersonaRegistry
from src.policy.enforcer import PolicyEnforcer
from src.orchestrator.agent import CarAgentOrchestrator

logger = structlog.get_logger()

# Initialize components
_policy = PolicyEnforcer()
_persona = PersonaRegistry(prompts_dir=settings.prompts_dir)
_orchestrator = CarAgentOrchestrator(
    persona_registry=_persona,
    policy_enforcer=_policy,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("agent_service_starting", port=settings.port)
    yield
    logger.info("agent_service_stopping")


app = FastAPI(
    title="Family Car Agent — Agent Service",
    version="0.1.0",
    lifespan=lifespan,
)


class ProcessRequest(BaseModel):
    actor_id: str
    transcript: str
    trip_id: str
    role_attrs: RoleAttributes | None = None
    context: dict | None = None


class ProcessResponse(BaseModel):
    actor_id: str
    text: str
    tool_used: str | None = None
    policy_blocked: bool = False
    persona_key: str = ""


class ConcurrentRequest(BaseModel):
    utterances: list[dict]
    trip_id: str
    context: dict | None = None


class PolicyEvalRequest(BaseModel):
    actor_id: str
    tool_name: str
    role_attrs: RoleAttributes
    context: dict | None = None


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent-service"}


@app.post("/agent/process")
async def process_utterance(
    request: ProcessRequest,
) -> ProcessResponse:
    """Process a single utterance — generate persona-appropriate response."""
    role_attrs = request.role_attrs or RoleAttributes()
    persona_key = _persona.get_persona_key(role_attrs)

    # Use real orchestrator with Strands Agent + Bedrock
    try:
        response_text = await _orchestrator.process(
            actor_id=request.actor_id,
            transcript=request.transcript,
            role_attrs=role_attrs,
            context=request.context,
        )
    except Exception as e:
        logger.error("orchestrator_error", error=str(e))
        response_text = "죄송합니다, 잠시 후 다시 말씀해주세요."

    logger.info(
        "utterance_processed",
        actor_id=request.actor_id,
        persona_key=persona_key,
        trip_id=request.trip_id,
    )

    return ProcessResponse(
        actor_id=request.actor_id,
        text=response_text,
        persona_key=persona_key,
    )


@app.post("/agent/concurrent")
async def process_concurrent(
    request: ConcurrentRequest,
) -> list[ProcessResponse]:
    """Process concurrent utterances with priority ordering."""
    # TODO: Implement priority sorting based on role_attrs + driving context
    responses = []
    for utt in request.utterances:
        resp = await process_utterance(
            ProcessRequest(
                actor_id=utt["actor_id"],
                transcript=utt["transcript"],
                trip_id=request.trip_id,
            ),
        )
        responses.append(resp)

    return responses


@app.post("/policy/evaluate")
async def evaluate_policy(
    request: PolicyEvalRequest,
) -> dict:
    """Evaluate tool permission for an actor."""
    decision = _policy.evaluate(
        role_attrs=request.role_attrs,
        tool_name=request.tool_name,
        context=request.context,
    )

    return {
        "allowed": decision.allowed,
        "rule_id": decision.rule_id,
        "reason": decision.reason,
    }


def _generate_placeholder_response(
    transcript: str,
    persona_key: str,
    style: ResponseStyle,
) -> str:
    """Generate placeholder response (replaced by Strands Agent + Bedrock)."""
    templates = {
        "driver_adult": f"[운전자 응답] '{transcript}'에 대한 효율적 답변입니다.",
        "passenger_adult": f"[동승자 응답] '{transcript}'에 대한 협업적 답변입니다.",
        "child": f"[어린이 응답] '{transcript}'에 대한 친근한 답변이야!",
        "elder": f"[어르신 응답] '{transcript}'에 대한 답변입니다.",
        "guest": f"[게스트 응답] '{transcript}'에 대한 정보입니다.",
    }
    return templates.get(persona_key, f"응답: {transcript}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
