"""Amazon Transcribe Streaming integration.

Modes:
- LIVE: Real-time audio → Transcribe Streaming → diarization results
- FALLBACK: Pre-recorded scenarios with mock diarization
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog

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


class TranscribeClient:
    """Manages Transcribe Streaming connection.

    Production: connects to Amazon Transcribe Streaming API.
    Fallback: returns pre-defined scenario results.
    """

    def __init__(
        self,
        mode: str = "FALLBACK",
    ) -> None:
        self._mode = mode
        self._connected = False
        self._failure_count = 0
        self._max_failures = 3

    @property
    def mode(self) -> str:
        return self._mode

    async def connect(self) -> bool:
        """Establish Transcribe Streaming connection."""
        if self._mode == "FALLBACK":
            self._connected = True
            logger.info("transcribe_fallback_mode")
            return True

        try:
            # TODO: Implement actual Transcribe Streaming connection
            # boto3 async transcribe streaming
            self._connected = True
            self._failure_count = 0
            logger.info("transcribe_connected", mode=self._mode)
            return True

        except Exception as e:
            self._failure_count += 1
            logger.error(
                "transcribe_connection_failed",
                error=str(e),
                failure_count=self._failure_count,
            )

            if self._failure_count >= self._max_failures:
                logger.warning("transcribe_switching_to_fallback")
                self._mode = "FALLBACK"
                self._connected = True
                return True

            return False

    async def disconnect(self) -> None:
        """Close Transcribe connection."""
        self._connected = False
        logger.info("transcribe_disconnected")

    async def process_audio(
        self,
        audio_data: bytes,
        seat_channel: int,
    ) -> TranscriptionEvent | None:
        """Process audio chunk and return transcription event.

        In FALLBACK mode, returns None (use send_mock_utterance instead).
        """
        if not self._connected:
            return None

        if self._mode == "LIVE":
            # TODO: Send audio to Transcribe Streaming
            # Return diarization result when available
            return None

        return None

    def create_mock_event(
        self,
        spk_label: str,
        transcript: str,
        seat_channel: int,
        confidence: float = 0.95,
    ) -> TranscriptionEvent:
        """Create a mock transcription event for testing/fallback."""
        return TranscriptionEvent(
            spk_label=spk_label,
            transcript=transcript,
            confidence=confidence,
            is_partial=False,
            seat_channel=seat_channel,
        )


# Pre-defined demo scenarios for FALLBACK mode
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
