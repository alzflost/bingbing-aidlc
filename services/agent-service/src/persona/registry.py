"""Persona Registry — maps role attributes to prompt templates and response styles.

Loads YAML prompt templates from shared/prompts/ directory.
Deterministic mapping: same role_attrs → same prompt (PBT-03 invariant).
"""

from __future__ import annotations

from pathlib import Path

import yaml
import structlog

from shared.models import ResponseStyle, RoleAttributes

logger = structlog.get_logger()


class PersonaRegistry:
    """Maps role attributes to persona prompt templates and response styles."""

    def __init__(
        self,
        prompts_dir: str | Path,
    ) -> None:
        self._prompts_dir = Path(prompts_dir)
        self._templates: dict[str, dict] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all YAML prompt templates from directory."""
        if not self._prompts_dir.exists():
            logger.warning(
                "prompts_dir_not_found",
                path=str(self._prompts_dir),
            )
            return

        for yaml_file in self._prompts_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                template = yaml.safe_load(f)
                persona_key = template.get("persona", yaml_file.stem)
                self._templates[persona_key] = template

        logger.info(
            "templates_loaded",
            count=len(self._templates),
            keys=list(self._templates.keys()),
        )

    def get_persona_key(
        self,
        role_attrs: RoleAttributes,
    ) -> str:
        """Determine persona key from role attributes.

        Deterministic mapping (PBT-03 invariant).
        """
        if role_attrs.driver and role_attrs.age_group == "adult":
            return "driver_adult"
        if role_attrs.age_group == "child":
            return "child"
        if role_attrs.age_group == "elder":
            return "elder"
        if role_attrs.relationship == "guest":
            return "guest"
        return "passenger_adult"

    def get_system_prompt(
        self,
        role_attrs: RoleAttributes,
        name: str = "",
        preferences_context: str = "",
        driving_state: str = "정차 중",
        passengers: str = "",
    ) -> str:
        """Get formatted system prompt for the given role attributes."""
        key = self.get_persona_key(role_attrs)
        template = self._templates.get(key, {})
        raw_prompt = template.get("system_prompt", "당신은 차량 AI 어시스턴트입니다.")

        return raw_prompt.format(
            name=name,
            preferences_context=preferences_context,
            driving_state=driving_state,
            passengers=passengers,
        )

    def get_response_style(
        self,
        role_attrs: RoleAttributes,
    ) -> ResponseStyle:
        """Get response style configuration for the given role attributes."""
        key = self.get_persona_key(role_attrs)
        template = self._templates.get(key, {})
        style_data = template.get("response_style", {})

        return ResponseStyle(
            tone=style_data.get("tone", "efficient"),
            verbosity=style_data.get("verbosity", "medium"),
            speech_rate=style_data.get("speech_rate", 1.0),
            honorific=style_data.get("honorific", "casual"),
            confirmation_required=style_data.get("confirmation_required", False),
        )
