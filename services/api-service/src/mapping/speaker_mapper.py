"""Speaker Mapper — 3-stage mapping strategy.

Stage 1: Seat channel mapping (driver auth + default_seat_channel)
Stage 2: Self-introduction binding (name matching against DDB profiles)
Stage 3: Heuristic (vocabulary/speech pattern → age_group estimation)
"""

from __future__ import annotations

import structlog

from shared.models import MappingState, TripSession, VehicleProfile

logger = structlog.get_logger()


class SpeakerMapper:
    """Maps Transcribe speaker labels (spk_N) to actor_ids using 3-stage strategy."""

    def __init__(
        self,
        session: TripSession,
        registered_profiles: list[VehicleProfile],
    ) -> None:
        self._session = session
        self._profiles = {p.actor_id: p for p in registered_profiles}
        self._profiles_by_name = {
            p.name.lower(): p for p in registered_profiles
        }
        self._profiles_by_channel = {
            p.default_seat_channel: p
            for p in registered_profiles
            if p.default_seat_channel is not None
        }

    @property
    def session(self) -> TripSession:
        return self._session

    def stage1_seat_channel(
        self,
        spk_label: str,
        seat_channel: int,
    ) -> str | None:
        """Stage 1: Map speaker by seat channel.

        Returns actor_id if channel matches a registered profile.
        """
        # Driver is already mapped via auth
        if seat_channel == 0 and self._session.driver_actor_id:
            actor_id = self._session.driver_actor_id
            self._bind(spk_label, actor_id)
            return actor_id

        # Check default_seat_channel for other profiles
        profile = self._profiles_by_channel.get(seat_channel)
        if profile:
            self._bind(spk_label, profile.actor_id)
            return profile.actor_id

        return None

    def stage2_introduction(
        self,
        spk_label: str,
        transcript: str,
    ) -> str | None:
        """Stage 2: Map speaker by self-introduction name matching.

        Returns actor_id if name found in registered profiles.
        """
        transcript_lower = transcript.lower().strip()

        for name, profile in self._profiles_by_name.items():
            if name in transcript_lower:
                self._bind(spk_label, profile.actor_id)
                logger.info(
                    "stage2_match",
                    spk_label=spk_label,
                    actor_id=profile.actor_id,
                    matched_name=name,
                )
                return profile.actor_id

        return None

    def stage3_heuristic(
        self,
        spk_label: str,
        transcript: str,
    ) -> str | None:
        """Stage 3: Estimate age_group from vocabulary/speech patterns.

        Returns a temporary actor_id based on heuristic classification.
        This is a simplified heuristic for MVP.
        """
        age_group = self._estimate_age_group(transcript)

        if age_group == "child":
            # Find unmatched child profile
            for profile in self._profiles.values():
                if (
                    profile.age_group == "child"
                    and profile.actor_id not in self._session.speaker_mappings.values()
                ):
                    self._bind(spk_label, profile.actor_id)
                    return profile.actor_id

        if age_group == "elder":
            for profile in self._profiles.values():
                if (
                    profile.age_group == "elder"
                    and profile.actor_id not in self._session.speaker_mappings.values()
                ):
                    self._bind(spk_label, profile.actor_id)
                    return profile.actor_id

        return None

    def assign_guest(
        self,
        spk_label: str,
    ) -> str:
        """Assign guest persona when all 3 stages fail."""
        guest_id = "actor_guest"
        self._bind(spk_label, guest_id)
        logger.info(
            "assigned_guest",
            spk_label=spk_label,
        )
        return guest_id

    def map_speaker(
        self,
        spk_label: str,
        transcript: str,
        seat_channel: int,
    ) -> str:
        """Execute full 3-stage mapping pipeline.

        Returns actor_id (always succeeds — falls back to guest).
        """
        # Already mapped?
        if spk_label in self._session.speaker_mappings:
            return self._session.speaker_mappings[spk_label]

        # Stage 1
        actor_id = self.stage1_seat_channel(spk_label, seat_channel)
        if actor_id:
            return actor_id

        # Stage 2
        actor_id = self.stage2_introduction(spk_label, transcript)
        if actor_id:
            return actor_id

        # Stage 3
        actor_id = self.stage3_heuristic(spk_label, transcript)
        if actor_id:
            return actor_id

        # Fallback: guest
        return self.assign_guest(spk_label)

    def _bind(
        self,
        spk_label: str,
        actor_id: str,
    ) -> None:
        """Bind speaker label to actor_id in session."""
        self._session.speaker_mappings[spk_label] = actor_id
        logger.info(
            "speaker_bound",
            spk_label=spk_label,
            actor_id=actor_id,
        )

    @staticmethod
    def _estimate_age_group(transcript: str) -> str | None:
        """Simple heuristic for age group estimation.

        MVP: keyword-based. Production: ML model.
        """
        child_indicators = ["엄마", "아빠", "놀이", "만화", "틀어줘", "심심해"]
        elder_indicators = ["여보", "줄여줘", "뭐라고", "천천히"]

        transcript_lower = transcript.lower()

        child_score = sum(
            1 for word in child_indicators if word in transcript_lower
        )
        elder_score = sum(
            1 for word in elder_indicators if word in transcript_lower
        )

        if child_score >= 2:
            return "child"
        if elder_score >= 2:
            return "elder"

        return None
