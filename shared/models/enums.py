"""Enumerations for Family Car Agent domain."""

from enum import StrEnum


class AgeGroup(StrEnum):
    ADULT = "adult"
    TEEN = "teen"
    CHILD = "child"
    ELDER = "elder"


class Relationship(StrEnum):
    OWNER = "owner"
    FAMILY = "family"
    GUEST = "guest"


class MappingState(StrEnum):
    IDLE = "idle"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    TRIP_END = "trip_end"
