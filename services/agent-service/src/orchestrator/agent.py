"""Strands Agent orchestrator with Bedrock Claude Haiku 4.5.

Responsibilities:
- Build persona-specific system prompt
- Invoke Claude via Strands Agent
- Handle tool calls with policy enforcement
- Return persona-styled response
"""

from __future__ import annotations

import structlog
from strands import Agent
from strands.models.bedrock import BedrockModel

from shared.models import RoleAttributes, ResponseStyle
from src.config import settings
from src.persona.registry import PersonaRegistry
from src.policy.enforcer import PolicyEnforcer
from src.orchestrator.tools import get_tools_for_role

logger = structlog.get_logger()


class CarAgentOrchestrator:
    """Main orchestrator using Strands Agent + Bedrock."""

    def __init__(
        self,
        persona_registry: PersonaRegistry,
        policy_enforcer: PolicyEnforcer,
    ) -> None:
        self._persona = persona_registry
        self._policy = policy_enforcer
        self._model = BedrockModel(
            model_id=settings.bedrock_model_id,
            region_name=settings.aws_region,
        )

    async def process(
        self,
        actor_id: str,
        transcript: str,
        role_attrs: RoleAttributes,
        name: str = "",
        preferences_context: str = "",
        driving_state: str = "정차 중",
        passengers: str = "",
        context: dict | None = None,
    ) -> str:
        """Process utterance and generate persona-appropriate response.

        Args:
            actor_id: Speaker's actor ID.
            transcript: What the speaker said.
            role_attrs: Speaker's current role attributes.
            name: Speaker's display name.
            preferences_context: LTM preferences summary.
            driving_state: Current driving state.
            passengers: Current passengers description.
            context: Additional context (driving_speed, etc.)

        Returns:
            Generated response text.
        """
        system_prompt = self._persona.get_system_prompt(
            role_attrs=role_attrs,
            name=name,
            preferences_context=preferences_context,
            driving_state=driving_state,
            passengers=passengers,
        )

        tools = get_tools_for_role(
            role_attrs=role_attrs,
            policy_enforcer=self._policy,
            context=context or {},
        )

        agent = Agent(
            model=self._model,
            system_prompt=system_prompt,
            tools=tools,
        )

        try:
            result = agent(transcript)
            response_text = str(result)

            logger.info(
                "agent_response_generated",
                actor_id=actor_id,
                persona_key=self._persona.get_persona_key(role_attrs),
                response_length=len(response_text),
            )

            return response_text

        except Exception as e:
            logger.error(
                "agent_invocation_failed",
                actor_id=actor_id,
                error=str(e),
            )
            # Fail-safe: return generic response
            return "죄송합니다, 잠시 후 다시 말씀해주세요."
