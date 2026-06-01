"""
Tool Registry — Declarative skill/tool registration for agents.

Usage:
    from agents._base.tool_registry import tool

    @tool(name="filesystem.read", requires_approval=False, side_effects="read_only")
    async def read_file(path: str) -> str:
        ...
"""
from __future__ import annotations

import functools
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

logger = logging.getLogger("arizen.tools")


@dataclass
class ToolMeta:
    name:               str
    description:        str       = ""
    requires_approval:  bool      = False
    side_effects:       str       = "read_only"   # read_only | idempotent | write | destructive | system
    schema:             dict      = field(default_factory=dict)


_REGISTRY: dict[str, ToolMeta] = {}


def tool(
    name:               str,
    description:        str  = "",
    requires_approval:  bool = False,
    side_effects:       str  = "read_only",
) -> Callable:
    """Decorator to register a function as a named tool."""
    def decorator(fn: Callable) -> Callable:
        meta = ToolMeta(
            name=name,
            description=description or fn.__doc__ or "",
            requires_approval=requires_approval,
            side_effects=side_effects,
        )
        _REGISTRY[name] = meta
        fn.__tool_meta__ = meta

        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug("Tool call: %s", name)
            return await fn(*args, **kwargs)

        return wrapper
    return decorator


def get_tool(name: str) -> ToolMeta | None:
    return _REGISTRY.get(name)


def list_tools() -> list[ToolMeta]:
    return list(_REGISTRY.values())
