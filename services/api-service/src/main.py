"""API Service — FastAPI application entry point."""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from shared.models import MappingState, TripSession, Utterance
from src.config import settings
from src.mapping.speaker_mapper import SpeakerMapper
from src.mapping.state_machine import get_next_state

logger = structlog.get_logger()

# In-memory state (production: Valkey)
_sessions: dict[str, TripSession] = {}
_mappers: dict[str, SpeakerMapper] = {}
_buffers: dict[str, list[Utterance]] = {}
_buffer_tasks: dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    logger.info("api_service_starting", port=settings.port)
    yield
    logger.info("api_service_stopping")


app = FastAPI(
    title="Family Car Agent — API Service",
    version="0.1.0",
    lifespan=lifespan,
)


class TripStartRequest(BaseModel):
    vehicle_id: str
    driver_actor_id: str
    seat_occupancy: dict[int, str | None]


class TripStartResponse(BaseModel):
    trip_id: str
    state: str


class ProcessRequest(BaseModel):
    trip_id: str
    spk_label: str
    transcript: str
    seat_channel: int


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-service"}


@app.post("/api/trip/start")
async def start_trip(
    request: TripStartRequest,
) -> TripStartResponse:
    """Start a new trip (시동 ON)."""
    trip_id = f"trip-{uuid.uuid4().hex[:8]}"

    session = TripSession(
        trip_id=trip_id,
        vehicle_id=request.vehicle_id,
        started_at=datetime.now(tz=timezone.utc),
        state=MappingState.ONBOARDING,
        seat_occupancy=request.seat_occupancy,
        driver_actor_id=request.driver_actor_id,
    )
    _sessions[trip_id] = session

    # TODO: Load registered profiles from DynamoDB
    _mappers[trip_id] = SpeakerMapper(
        session=session,
        registered_profiles=[],
    )

    logger.info(
        "trip_started",
        trip_id=trip_id,
        vehicle_id=request.vehicle_id,
        driver=request.driver_actor_id,
    )

    return TripStartResponse(trip_id=trip_id, state=session.state)


@app.post("/api/trip/end")
async def end_trip(
    trip_id: str,
):
    """End a trip (시동 OFF)."""
    session = _sessions.get(trip_id)
    if not session:
        return {"error": "trip not found"}

    new_state = get_next_state(session.state, "trip_end")
    if new_state:
        session.state = new_state

    # TODO: Publish trip.ended event to EventBridge
    logger.info("trip_ended", trip_id=trip_id)

    return {"trip_id": trip_id, "state": session.state}


@app.post("/api/process")
async def process_utterance(
    request: ProcessRequest,
):
    """Process a single utterance — map speaker + forward to agent."""
    session = _sessions.get(request.trip_id)
    if not session:
        return {"error": "trip not found"}

    mapper = _mappers.get(request.trip_id)
    if not mapper:
        return {"error": "mapper not found"}

    # Map speaker
    actor_id = mapper.map_speaker(
        spk_label=request.spk_label,
        transcript=request.transcript,
        seat_channel=request.seat_channel,
    )

    # Buffer for concurrent speech (500ms window)
    utterance = Utterance(
        utterance_id=f"utt-{uuid.uuid4().hex[:8]}",
        trip_id=request.trip_id,
        actor_id=actor_id,
        spk_label=request.spk_label,
        transcript=request.transcript,
        timestamp=datetime.now(tz=timezone.utc),
        seat_channel=request.seat_channel,
    )

    return await _buffer_and_process(utterance)


async def _buffer_and_process(
    utterance: Utterance,
) -> dict:
    """Buffer utterances for 500ms concurrent speech detection."""
    trip_id = utterance.trip_id

    if trip_id not in _buffers:
        _buffers[trip_id] = []

    _buffers[trip_id].append(utterance)

    # Cancel existing timer and restart
    if trip_id in _buffer_tasks:
        _buffer_tasks[trip_id].cancel()

    _buffer_tasks[trip_id] = asyncio.create_task(
        _flush_buffer(trip_id),
    )

    return {
        "status": "buffered",
        "actor_id": utterance.actor_id,
        "utterance_id": utterance.utterance_id,
    }


async def _flush_buffer(
    trip_id: str,
) -> None:
    """Flush buffer after 500ms window."""
    await asyncio.sleep(0.5)

    buffered = _buffers.pop(trip_id, [])
    _buffer_tasks.pop(trip_id, None)

    if not buffered:
        return

    # Forward to Agent Service
    async with httpx.AsyncClient(timeout=10.0) as client:
        if len(buffered) == 1:
            # Single utterance
            await client.post(
                f"{settings.agent_service_url}/agent/process",
                json={
                    "actor_id": buffered[0].actor_id,
                    "transcript": buffered[0].transcript,
                    "trip_id": trip_id,
                },
            )
        else:
            # Concurrent utterances
            await client.post(
                f"{settings.agent_service_url}/agent/concurrent",
                json={
                    "utterances": [
                        {
                            "actor_id": u.actor_id,
                            "transcript": u.transcript,
                        }
                        for u in buffered
                    ],
                    "trip_id": trip_id,
                },
            )


@app.websocket("/ws/trip")
async def websocket_trip(
    ws: WebSocket,
):
    """WebSocket endpoint for real-time trip communication."""
    await ws.accept()
    logger.info("ws_connected")

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "trip_start":
                result = await start_trip(TripStartRequest(**data))
                await ws.send_json({"type": "trip_started", **result.model_dump()})

            elif msg_type == "utterance":
                result = await process_utterance(ProcessRequest(**data))
                await ws.send_json({"type": "utterance_processed", **result})

            elif msg_type == "trip_end":
                result = await end_trip(data.get("trip_id", ""))
                await ws.send_json({"type": "trip_ended", **result})

    except WebSocketDisconnect:
        logger.info("ws_disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
