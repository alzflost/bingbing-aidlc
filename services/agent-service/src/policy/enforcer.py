"""Policy Enforcer — Role-based permission evaluation.

Evaluates tool access permissions based on role attributes.
Production: delegates to AgentCore Policy (Verified Permissions).
Local/test: uses in-process rule evaluation.
"""

from __future__ import annotations

import structlog

from shared.models import PolicyDecision, RoleAttributes

logger = structlog.get_logger()

# Tool categories for policy evaluation
SAFETY_TOOLS = frozenset({"vehicle_drive_control", "navigation"})
CONTROL_TOOLS = frozenset({"vehicle_drive_control", "seat_control", "navigation"})
COMMUNICATION_TOOLS = frozenset({"bt_call"})
CONTENT_TOOLS = frozenset({"music", "web_search"})


class PolicyEnforcer:
    """Evaluates permissions based on role attributes and context."""

    def evaluate(
        self,
        role_attrs: RoleAttributes,
        tool_name: str,
        context: dict | None = None,
    ) -> PolicyDecision:
        """Evaluate whether the actor can use the specified tool.

        Args:
            role_attrs: Actor's current role attributes.
            tool_name: Name of the tool being requested.
            context: Additional context (driving_speed, etc.)

        Returns:
            PolicyDecision with allowed/denied and reason.
        """
        ctx = context or {}
        driving_speed = ctx.get("driving_speed", 0)
        confirmation_received = ctx.get("confirmation_received", False)

        decision = self._evaluate_rules(
            role_attrs=role_attrs,
            tool_name=tool_name,
            driving_speed=driving_speed,
            confirmation_received=confirmation_received,
        )

        logger.info(
            "policy_evaluated",
            actor_driver=role_attrs.driver,
            actor_age_group=role_attrs.age_group,
            actor_relationship=role_attrs.relationship,
            tool=tool_name,
            allowed=decision.allowed,
            rule_id=decision.rule_id,
        )

        return decision

    def _evaluate_rules(
        self,
        role_attrs: RoleAttributes,
        tool_name: str,
        driving_speed: int,
        confirmation_received: bool,
    ) -> PolicyDecision:
        """Apply permission rules in priority order."""
        base = {
            "actor_id": "",
            "tool_name": tool_name,
            "context": {
                "driving_speed": driving_speed,
                "confirmation_received": confirmation_received,
            },
        }

        # Rule 1: Driver (adult) has full access
        if role_attrs.driver and role_attrs.age_group == "adult":
            return PolicyDecision(
                allowed=True,
                rule_id="PERMIT_DRIVER_ADULT",
                **base,
            )

        # Rule 2: Guest — only web_search
        if role_attrs.relationship == "guest":
            if tool_name == "web_search":
                return PolicyDecision(
                    allowed=True,
                    rule_id="PERMIT_GUEST_SEARCH",
                    **base,
                )
            return PolicyDecision(
                allowed=False,
                rule_id="DENY_GUEST_CONTROL",
                reason="게스트는 정보 조회만 가능합니다.",
                **base,
            )

        # Rule 3: Child restrictions
        if role_attrs.age_group == "child":
            return self._evaluate_child_rules(
                tool_name=tool_name,
                driving_speed=driving_speed,
                base=base,
            )

        # Rule 4: Elder restrictions
        if role_attrs.age_group == "elder":
            return self._evaluate_elder_rules(
                tool_name=tool_name,
                confirmation_received=confirmation_received,
                base=base,
            )

        # Rule 5: Adult family passenger — all except drive control
        if tool_name == "vehicle_drive_control":
            return PolicyDecision(
                allowed=False,
                rule_id="DENY_PASSENGER_DRIVE",
                reason="차량 운전 제어는 운전자만 가능합니다.",
                **base,
            )

        return PolicyDecision(
            allowed=True,
            rule_id="PERMIT_ADULT_FAMILY",
            **base,
        )

    def _evaluate_child_rules(
        self,
        tool_name: str,
        driving_speed: int,
        base: dict,
    ) -> PolicyDecision:
        """Child-specific permission rules."""
        # Absolute deny: drive control, navigation, phone
        if tool_name in {"vehicle_drive_control", "navigation", "bt_call"}:
            return PolicyDecision(
                allowed=False,
                rule_id="DENY_CHILD_CONTROL",
                reason="어린이는 이 기능을 사용할 수 없어요.",
                **base,
            )

        # Seat control: only when stopped
        if tool_name == "seat_control":
            if driving_speed > 0:
                return PolicyDecision(
                    allowed=False,
                    rule_id="DENY_CHILD_SEAT_DRIVING",
                    reason="지금 달리고 있어서 위험해. 도착하면 해줄게!",
                    **base,
                )
            return PolicyDecision(
                allowed=True,
                rule_id="PERMIT_CHILD_SEAT_STOPPED",
                reason="정차 중 — 부모 확인 필요",
                **base,
            )

        # Music/search: allowed with filters (filter logic in tool layer)
        if tool_name in {"music", "web_search"}:
            return PolicyDecision(
                allowed=True,
                rule_id="PERMIT_CHILD_CONTENT_FILTERED",
                **base,
            )

        return PolicyDecision(
            allowed=False,
            rule_id="DENY_CHILD_DEFAULT",
            reason="어린이는 이 기능을 사용할 수 없어요.",
            **base,
        )

    def _evaluate_elder_rules(
        self,
        tool_name: str,
        confirmation_received: bool,
        base: dict,
    ) -> PolicyDecision:
        """Elder-specific permission rules."""
        # Deny: drive control, navigation
        if tool_name in {"vehicle_drive_control", "navigation"}:
            return PolicyDecision(
                allowed=False,
                rule_id="DENY_ELDER_CONTROL",
                reason="죄송합니다, 이 기능은 운전자분께 부탁드릴게요.",
                **base,
            )

        # Phone: requires confirmation
        if tool_name == "bt_call":
            if not confirmation_received:
                return PolicyDecision(
                    allowed=False,
                    rule_id="DENY_ELDER_CALL_NO_CONFIRM",
                    reason="전화를 걸까요? 확인해주세요.",
                    **base,
                )
            return PolicyDecision(
                allowed=True,
                rule_id="PERMIT_ELDER_CALL_CONFIRMED",
                **base,
            )

        # Everything else: allowed
        return PolicyDecision(
            allowed=True,
            rule_id="PERMIT_ELDER_DEFAULT",
            **base,
        )
