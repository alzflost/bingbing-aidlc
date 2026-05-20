"""API Service — FastAPI application entry point."""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from shared.models import MappingState, TripSession, Utterance
from src.config import settings
from src.mapping.speaker_mapper import SpeakerMapper
from src.mapping.state_machine import get_next_state
from src.voice.transcribe import TranscribeClient, TranscriptionEvent

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

    from shared.models import VehicleProfile

    demo_profiles = [
        VehicleProfile(
            vehicle_id=request.vehicle_id,
            actor_id="actor_father",
            name="아빠",
            age_group="adult",
            relationship="owner",
            account_owner=True,
            default_seat_channel=0,
            preferences_summary="고기 좋아함, 운전 중 간결한 응답 선호",
        ),
        VehicleProfile(
            vehicle_id=request.vehicle_id,
            actor_id="actor_mother",
            name="엄마",
            age_group="adult",
            relationship="family",
            account_owner=False,
            default_seat_channel=1,
            preferences_summary="비건 선호, 건강식 관심",
        ),
        VehicleProfile(
            vehicle_id=request.vehicle_id,
            actor_id="actor_child_1",
            name="민수",
            age_group="child",
            relationship="family",
            account_owner=False,
            default_seat_channel=2,
            preferences_summary="공룡 좋아함, 만화 좋아함",
        ),
        VehicleProfile(
            vehicle_id=request.vehicle_id,
            actor_id="actor_elder_1",
            name="할머니",
            age_group="elder",
            relationship="family",
            account_owner=False,
            default_seat_channel=3,
            preferences_summary="느린 말투 선호, 큰 소리 싫어함",
        ),
    ]

    _mappers[trip_id] = SpeakerMapper(
        session=session,
        registered_profiles=demo_profiles,
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

    trip_id: str | None = None
    transcribe = TranscribeClient(mode=settings.transcribe_mode)

    async def on_transcription(event: TranscriptionEvent):
        """Callback when Transcribe returns a result."""
        if not trip_id:
            return
        # Process through speaker mapping + agent
        try:
            result = await process_utterance(ProcessRequest(
                trip_id=trip_id,
                spk_label=event.spk_label,
                transcript=event.transcript,
                seat_channel=event.seat_channel,
            ))
            await ws.send_json({"type": "utterance_processed", **result})

            # Forward to agent
            async with httpx.AsyncClient(timeout=10.0) as client:
                agent_resp = await client.post(
                    f"{settings.agent_service_url}/agent/process",
                    json={
                        "actor_id": result.get("actor_id", ""),
                        "transcript": event.transcript,
                        "trip_id": trip_id,
                    },
                )
                if agent_resp.status_code == 200:
                    agent_data = agent_resp.json()
                    await ws.send_json({
                        "type": "agent_response",
                        "payload": {
                            "id": f"resp-{uuid.uuid4().hex[:8]}",
                            "type": "agent_response",
                            "actor_id": agent_data.get("actor_id", "agent"),
                            "text": agent_data.get("text", ""),
                            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                            "tool_used": agent_data.get("tool_used"),
                            "policy_decision": None,
                        },
                    })
        except Exception as e:
            logger.error("transcription_processing_error", error=str(e))

    try:
        while True:
            message = await ws.receive()

            if message.get("type") == "websocket.disconnect":
                break

            # Binary = audio data → send to Transcribe
            if "bytes" in message:
                await transcribe.send_audio(message["bytes"])
                continue

            # JSON = control messages
            if "text" in message:
                import json
                data = json.loads(message["text"])
                msg_type = data.get("type")

                if msg_type == "trip_start":
                    result = await start_trip(TripStartRequest(**data))
                    trip_id = result.trip_id
                    await transcribe.connect(callback=on_transcription)
                    await ws.send_json({"type": "trip_started", **result.model_dump()})

                elif msg_type == "utterance":
                    # Text-based utterance (fallback / text input)
                    data["trip_id"] = data.get("trip_id") or trip_id
                    result = await process_utterance(ProcessRequest(**data))
                    await ws.send_json({"type": "utterance_processed", **result})

                    # Build role_attrs from mapped actor
                    actor_id = result.get("actor_id", "unknown")
                    role_attrs = None
                    if trip_id and trip_id in _mappers:
                        mapper = _mappers[trip_id]
                        for p in mapper._profiles.values():
                            if p.actor_id == actor_id:
                                role_attrs = {
                                    "driver": actor_id == _sessions[trip_id].driver_actor_id,
                                    "age_group": str(p.age_group),
                                    "relationship": str(p.relationship),
                                    "account_owner": p.account_owner,
                                }
                                break

                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            agent_resp = await client.post(
                                f"{settings.agent_service_url}/agent/process",
                                json={
                                    "actor_id": actor_id,
                                    "transcript": data.get("transcript", ""),
                                    "trip_id": trip_id or "",
                                    "role_attrs": role_attrs,
                                },
                            )
                            if agent_resp.status_code == 200:
                                agent_data = agent_resp.json()
                                await ws.send_json({
                                    "type": "agent_response",
                                    "payload": {
                                        "id": f"resp-{uuid.uuid4().hex[:8]}",
                                        "type": "agent_response",
                                        "actor_id": agent_data.get("actor_id", "agent"),
                                        "text": agent_data.get("text", ""),
                                        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                                        "tool_used": agent_data.get("tool_used"),
                                        "policy_decision": None,
                                    },
                                })
                    except Exception as e:
                        logger.error("agent_forward_error", error=str(e))

                elif msg_type == "trip_end":
                    await transcribe.disconnect()
                    result = await end_trip(data.get("trip_id", ""))
                    await ws.send_json({"type": "trip_ended", **result})

    except WebSocketDisconnect:
        await transcribe.disconnect()
        logger.info("ws_disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )

# Static file serving (React frontend)
from pathlib import Path

_static_dir = Path("/app/static")
if not _static_dir.exists():
    _static_dir = Path(__file__).parent.parent / "static"

if _static_dir.exists() and (_static_dir / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=_static_dir / "assets"), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(_static_dir / "index.html")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        file_path = _static_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_static_dir / "index.html")
