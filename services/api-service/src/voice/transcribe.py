"""Amazon Transcribe Streaming integration.

Uses boto3 async to stream audio and receive real-time transcription
with speaker diarization.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass

import boto3
import structlog
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

from src.config import settings

logger = structlog.get_logger()


@dataclass
class TranscriptionEvent:
    """A transcription result with speaker diarization."""

    spk_label: str
    transcript: str
    confidence: float
    is_partial: bool
    seat_channel: int


class TranscribeStreamHandler(TranscriptResultStreamHandler):
    """Handle Transcribe streaming results."""

    def __init__(self, output_stream, callback):
        super().__init__(output_stream)
        self._callback = callback

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                continue
            for alt in result.alternatives:
                transcript = alt.transcript.strip()
                if not transcript:
                    continue
                # Extract speaker label from items if available
                spk_label = "spk_0"
                for item in alt.items:
                    if hasattr(item, 'speaker') and item.speaker is not None:
                        spk_label = f"spk_{item.speaker}"
                        break

                event = TranscriptionEvent(
                    spk_label=spk_label,
                    transcript=transcript,
                    confidence=alt.items[0].confidence if alt.items else 0.95,
                    is_partial=False,
                    seat_channel=0,
                )
                await self._callback(event)


class TranscribeClient:
    """Manages Transcribe Streaming connection."""

    def __init__(self, mode: str = "FALLBACK") -> None:
        self._mode = mode
        self._connected = False
        self._client = None
        self._stream = None
        self._callback = None

    @property
    def mode(self) -> str:
        return self._mode

    async def connect(self, callback=None) -> bool:
        """Establish Transcribe Streaming connection."""
        self._callback = callback

        if self._mode == "FALLBACK":
            self._connected = True
            logger.info("transcribe_fallback_mode")
            return True

        try:
            self._client = TranscribeStreamingClient(region=settings.aws_region)
            self._stream = await self._client.start_stream_transcription(
                language_code="ko-KR",
                media_sample_rate_hz=16000,
                media_encoding="pcm",
                show_speaker_label=True,
                number_of_channels=1,
            )
            self._connected = True
            logger.info("transcribe_connected", mode=self._mode)

            # Start handler in background
            if self._callback:
                handler = TranscribeStreamHandler(
                    self._stream.output_stream, self._callback
                )
                asyncio.create_task(handler.handle_events())

            return True
        except Exception as e:
            logger.error("transcribe_connection_failed", error=str(e))
            logger.warning("transcribe_switching_to_fallback")
            self._mode = "FALLBACK"
            self._connected = True
            return True

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio chunk to Transcribe stream."""
        if self._mode == "LIVE" and self._stream:
            await self._stream.input_stream.send_audio_event(audio_chunk=audio_data)

    async def disconnect(self) -> None:
        """Close Transcribe connection."""
        if self._stream and self._mode == "LIVE":
            await self._stream.input_stream.end_stream()
        self._connected = False
        logger.info("transcribe_disconnected")

    def create_mock_event(
        self,
        spk_label: str,
        transcript: str,
        seat_channel: int,
        confidence: float = 0.95,
    ) -> TranscriptionEvent:
        """Create a mock transcription event for fallback mode."""
        return TranscriptionEvent(
            spk_label=spk_label,
            transcript=transcript,
            confidence=confidence,
            is_partial=False,
            seat_channel=seat_channel,
        )


DEMO_SCENARIOS = {
    "s1_welcome": [
        {"spk_label": "spk_0", "transcript": "오늘 장모님 댁 가는 길 어때?", "seat_channel": 0},
        {"spk_label": "spk_2", "transcript": "아빠 나 심심해", "seat_channel": 2},
    ],
    "s3_same_word": [
        {"spk_label": "spk_1", "transcript": "배고프다", "seat_channel": 1},
        {"spk_label": "spk_0", "transcript": "배고프다", "seat_channel": 0},
    ],
    "s4_child_safety": [
        {"spk_label": "spk_2", "transcript": "창문 열어줘", "seat_channel": 2},
        {"spk_label": "spk_2", "transcript": "엄마한테 전화 걸어줘", "seat_channel": 2},
    ],
}
