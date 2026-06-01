"""
Skill SDK — Base class and decorator for atomic ArizenOS skills.

A skill is a STATELESS, single-purpose function with a declared side-effect
profile and an optional approval requirement. Skills are the leaf nodes in the
agent action tree — agents compose skills, not the reverse.

Design rules:
  - Skills NEVER read or write to memory/ (use agents for stateful ops)
  - Skills NEVER call other skills directly (compose in agents/playbooks)
  - Skills MUST declare their side_effects in the manifest
  - Skills MAY be called by agents, playbooks, or directly from the CLI
"""
from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("arizen.skills")


@dataclass
class SkillManifest:
    name:               str
    description:        str
    category:           str            # filesystem | shell | clipboard | browser | windows
    side_effects:       str            # read_only | idempotent | write | destructive | system
    requires_approval:  bool           = False
    input_schema:       dict           = field(default_factory=dict)
    output_schema:      dict           = field(default_factory=dict)
    platforms:          list[str]      = field(default_factory=lambda: ["windows"])


class BaseSkill(abc.ABC):
    """Abstract base for all skills."""

    MANIFEST: SkillManifest

    @abc.abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """Execute the skill with validated inputs."""
        ...

    async def __call__(self, **kwargs: Any) -> Any:
        logger.debug("Skill: %s | inputs: %s", self.MANIFEST.name, list(kwargs.keys()))
        return await self.run(**kwargs)

    @classmethod
    def describe(cls) -> dict:
        m = cls.MANIFEST
        return {
            "name":               m.name,
            "description":        m.description,
            "category":           m.category,
            "side_effects":       m.side_effects,
            "requires_approval":  m.requires_approval,
        }
