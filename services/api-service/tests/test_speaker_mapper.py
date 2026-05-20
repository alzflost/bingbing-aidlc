"""Unit tests for Speaker Mapper — 3-stage mapping strategy.

PBT-03: Invariant — same spk_label always maps to same actor_id.
PBT-03: Invariant — map_speaker always returns a non-empty string.
"""

from datetime import datetime, timezone

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import MappingState, TripSession, VehicleProfile
from src.mapping.speaker_mapper import SpeakerMapper


def _make_session(
    driver_actor_id: str = "actor_father",
) -> TripSession:
    return TripSession(
        trip_id="trip-001",
        vehicle_id="vehicle-001",
        started_at=datetime.now(tz=timezone.utc),
        state=MappingState.ACTIVE,
        driver_actor_id=driver_actor_id,
    )


def _make_profiles() -> list[VehicleProfile]:
    return [
        VehicleProfile(
            vehicle_id="vehicle-001",
            actor_id="actor_father",
            name="아빠",
            age_group="adult",
            relationship="owner",
            account_owner=True,
            default_seat_channel=0,
        ),
        VehicleProfile(
            vehicle_id="vehicle-001",
            actor_id="actor_mother",
            name="엄마",
            age_group="adult",
            relationship="family",
            default_seat_channel=1,
        ),
        VehicleProfile(
            vehicle_id="vehicle-001",
            actor_id="actor_child_1",
            name="민수",
            age_group="child",
            relationship="family",
            default_seat_channel=2,
        ),
        VehicleProfile(
            vehicle_id="vehicle-001",
            actor_id="actor_elder_1",
            name="할머니",
            age_group="elder",
            relationship="family",
            default_seat_channel=3,
        ),
    ]


class TestStage1SeatChannel:
    """Stage 1: Seat channel mapping."""

    def test_driver_seat_maps_to_driver(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage1_seat_channel("spk_0", seat_channel=0)
        assert result == "actor_father"

    def test_passenger_seat_maps_to_registered_profile(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage1_seat_channel("spk_1", seat_channel=1)
        assert result == "actor_mother"

    def test_unknown_channel_returns_none(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage1_seat_channel("spk_4", seat_channel=5)
        assert result is None


class TestStage2Introduction:
    """Stage 2: Self-introduction name matching."""

    def test_name_match_returns_actor_id(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage2_introduction("spk_2", "나 민수야")
        assert result == "actor_child_1"

    def test_partial_name_match(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage2_introduction("spk_3", "할머니예요")
        assert result == "actor_elder_1"

    def test_no_match_returns_none(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage2_introduction("spk_4", "안녕하세요 철수입니다")
        assert result is None


class TestStage3Heuristic:
    """Stage 3: Vocabulary/speech pattern heuristic."""

    def test_child_indicators_detected(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage3_heuristic("spk_2", "엄마 만화 틀어줘")
        assert result == "actor_child_1"

    def test_elder_indicators_detected(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage3_heuristic("spk_3", "여보 에어컨 줄여줘")
        assert result == "actor_elder_1"

    def test_no_indicators_returns_none(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.stage3_heuristic("spk_4", "오늘 날씨 어때")
        assert result is None


class TestFullPipeline:
    """Full 3-stage mapping pipeline."""

    def test_driver_mapped_via_stage1(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.map_speaker("spk_0", "경로 안내해줘", seat_channel=0)
        assert result == "actor_father"

    def test_unknown_speaker_becomes_guest(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.map_speaker("spk_4", "안녕하세요", seat_channel=5)
        assert result == "actor_guest"

    def test_already_mapped_returns_cached(self) -> None:
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        mapper.map_speaker("spk_0", "첫 발화", seat_channel=0)
        result = mapper.map_speaker("spk_0", "두번째 발화", seat_channel=0)
        assert result == "actor_father"


class TestSpeakerMapperPBT:
    """Property-based tests (PBT-03)."""

    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("L", "N")),
            min_size=1,
            max_size=20,
        ),
        st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=100)
    def test_map_speaker_always_returns_string(
        self,
        transcript: str,
        seat_channel: int,
    ) -> None:
        """Invariant: map_speaker always returns a non-empty actor_id."""
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        result = mapper.map_speaker("spk_test", transcript, seat_channel)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_same_speaker_always_same_actor(self) -> None:
        """Invariant: once mapped, same spk_label → same actor_id."""
        mapper = SpeakerMapper(_make_session(), _make_profiles())
        first = mapper.map_speaker("spk_0", "안녕", seat_channel=0)
        second = mapper.map_speaker("spk_0", "다른 말", seat_channel=0)
        assert first == second
