"""Strands Tools for the Car Agent.

Tools are filtered per role_attrs via policy enforcement.
Real: web_search (via Tavily/httpx)
Mock: navigation, vehicle_control, seat_control, music, bt_call
"""

from __future__ import annotations

from typing import Annotated

import httpx
import structlog
from strands import tool

from shared.models import RoleAttributes
from src.policy.enforcer import PolicyEnforcer

logger = structlog.get_logger()


# --- Mock Tools ---

@tool
def navigate_to(
    destination: Annotated[str, "목적지 이름 또는 주소"],
) -> str:
    """차량 내비게이션 목적지를 설정합니다."""
    return f"목적지 '{destination}'으로 경로를 설정했습니다. 예상 소요시간: 25분."


@tool
def control_vehicle(
    action: Annotated[str, "차량 제어 동작 (예: 창문열기, 에어컨조절)"],
    value: Annotated[str, "제어 값 (예: 열기, 24도)"] = "",
) -> str:
    """차량을 제어합니다 (창문, 에어컨 등)."""
    return f"차량 제어 완료: {action} {value}"


@tool
def control_seat(
    action: Annotated[str, "좌석 환경 제어 (예: 온도올리기, 시트히터)"],
    seat: Annotated[str, "좌석 위치 (운전석/조수석/뒷좌석)"] = "본인좌석",
) -> str:
    """좌석 환경을 제어합니다."""
    return f"{seat} {action} 완료."


@tool
def play_music(
    query: Annotated[str, "재생할 음악 또는 장르"],
) -> str:
    """음악을 재생합니다."""
    return f"'{query}' 재생을 시작합니다."


@tool
def make_call(
    contact: Annotated[str, "전화할 연락처 이름 또는 번호"],
) -> str:
    """블루투스 전화를 겁니다."""
    return f"{contact}에게 전화를 겁니다..."


@tool
def search_web(
    query: Annotated[str, "검색할 내용"],
) -> str:
    """웹에서 정보를 검색합니다."""
    # TODO: Replace with actual Tavily/Brave API call
    return f"'{query}' 검색 결과: 관련 정보를 찾았습니다."


# --- Tool Registry ---

_ALL_TOOLS = {
    "navigation": navigate_to,
    "vehicle_drive_control": control_vehicle,
    "seat_control": control_seat,
    "music": play_music,
    "bt_call": make_call,
    "web_search": search_web,
}

_TOOL_NAMES = {
    navigate_to: "navigation",
    control_vehicle: "vehicle_drive_control",
    control_seat: "seat_control",
    play_music: "music",
    make_call: "bt_call",
    search_web: "web_search",
}


def get_tools_for_role(
    role_attrs: RoleAttributes,
    policy_enforcer: PolicyEnforcer,
    context: dict,
) -> list:
    """Return list of tools allowed for the given role attributes.

    Filters tools based on policy evaluation.
    """
    allowed_tools = []

    for tool_name, tool_fn in _ALL_TOOLS.items():
        decision = policy_enforcer.evaluate(
            role_attrs=role_attrs,
            tool_name=tool_name,
            context=context,
        )
        if decision.allowed:
            allowed_tools.append(tool_fn)

    logger.info(
        "tools_filtered",
        role_driver=role_attrs.driver,
        role_age_group=role_attrs.age_group,
        allowed_count=len(allowed_tools),
        total_count=len(_ALL_TOOLS),
    )

    return allowed_tools
