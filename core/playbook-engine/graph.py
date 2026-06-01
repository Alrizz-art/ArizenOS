"""
Execution Graph — builds and orders a Playbook DAG.

Responsibilities:
  - Topological sort (Kahn's algorithm)
  - Cycle detection with descriptive error
  - Wave decomposition: groups of steps that can run in parallel
  - Critical path calculation for ETA estimation
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Optional

from playbooks.schema.playbook_schema import Playbook, Step


@dataclass
class Wave:
    """A set of steps that can execute in parallel."""
    index:  int
    steps:  list[Step] = field(default_factory=list)

    @property
    def step_ids(self) -> list[str]:
        return [s.id for s in self.steps]


@dataclass
class ExecutionGraph:
    """Ordered, validated execution plan derived from a Playbook."""
    playbook:        Playbook
    waves:           list[Wave]            = field(default_factory=list)
    id_to_step:      dict[str, Step]       = field(default_factory=dict)
    critical_path:   list[str]             = field(default_factory=list)
    estimated_sec:   float                 = 0.0

    def all_steps_flat(self) -> list[Step]:
        return [s for wave in self.waves for s in wave.steps]

    def step(self, sid: str) -> Optional[Step]:
        return self.id_to_step.get(sid)

    def dependents_of(self, sid: str) -> list[Step]:
        """Steps that depend on sid completing."""
        return [s for s in self.all_steps_flat() if sid in s.depends_on]

    def ancestors_of(self, sid: str) -> list[str]:
        """All transitive dependencies of a step (recursive)."""
        result: set[str] = set()
        queue = deque(self.id_to_step[sid].depends_on if sid in self.id_to_step else [])
        while queue:
            dep = queue.popleft()
            if dep not in result:
                result.add(dep)
                queue.extend(self.id_to_step[dep].depends_on)
        return list(result)


class GraphBuilder:
    """
    Builds an ExecutionGraph from a validated Playbook.
    
    Usage:
        graph = GraphBuilder().build(playbook)
        for wave in graph.waves:
            # run wave.steps in parallel
    """

    def build(self, playbook: Playbook) -> ExecutionGraph:
        id_to_step = {s.id: s for s in playbook.steps}
        self._assert_no_cycles(id_to_step)

        waves = self._kahn_waves(playbook.steps, id_to_step)
        cp    = self._critical_path(playbook.steps, id_to_step)
        eta   = sum(id_to_step[sid].timeout_sec for sid in cp)

        return ExecutionGraph(
            playbook=playbook,
            waves=waves,
            id_to_step=id_to_step,
            critical_path=cp,
            estimated_sec=eta,
        )

    # ------------------------------------------------------------------
    # Kahn's algorithm — wave decomposition
    # ------------------------------------------------------------------

    def _kahn_waves(self, steps: list[Step], id_to_step: dict[str, Step]) -> list[Wave]:
        """
        Groups steps into waves of independent, parallel-executable tasks.
        Wave N completes before Wave N+1 starts. Within a wave, all steps run concurrently.
        """
        in_degree: dict[str, int] = {s.id: len(s.depends_on) for s in steps}
        waves: list[Wave] = []
        remaining = set(id_to_step.keys())

        while remaining:
            # Ready = steps with all dependencies already in a previous wave
            completed = {s.id for wave in waves for s in wave.steps}
            ready = sorted(
                [sid for sid in remaining
                 if all(dep in completed for dep in id_to_step[sid].depends_on)],
                key=lambda sid: -id_to_step[sid].priority,  # higher priority first
            )
            if not ready:
                raise RuntimeError(
                    f"Execution graph stalled — possible cycle among: {remaining}. "
                    "Run PlaybookValidator first to catch cycles."
                )
            wave = Wave(index=len(waves), steps=[id_to_step[sid] for sid in ready])
            waves.append(wave)
            remaining -= set(ready)

        return waves

    # ------------------------------------------------------------------
    # Cycle detection — DFS
    # ------------------------------------------------------------------

    def _assert_no_cycles(self, id_to_step: dict[str, Step]) -> None:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {sid: WHITE for sid in id_to_step}

        def visit(node: str, path: list[str]) -> None:
            color[node] = GRAY
            for dep in id_to_step[node].depends_on:
                if dep not in color:
                    continue
                if color[dep] == GRAY:
                    cycle = path[path.index(dep):] + [dep]
                    raise ValueError(
                        f"Circular dependency: {' → '.join(cycle)}. "
                        "Fix depends_on in your playbook YAML."
                    )
                if color[dep] == WHITE:
                    visit(dep, path + [dep])
            color[node] = BLACK

        for sid in id_to_step:
            if color[sid] == WHITE:
                visit(sid, [sid])

    # ------------------------------------------------------------------
    # Critical path — longest chain by estimated timeout
    # ------------------------------------------------------------------

    def _critical_path(self, steps: list[Step], id_to_step: dict[str, Step]) -> list[str]:
        memo: dict[str, tuple[float, list[str]]] = {}

        def longest(sid: str) -> tuple[float, list[str]]:
            if sid in memo:
                return memo[sid]
            step    = id_to_step[sid]
            deps    = step.depends_on
            if not deps:
                memo[sid] = (step.timeout_sec, [sid])
                return memo[sid]
            best_t, best_path = 0.0, []
            for dep in deps:
                t, path = longest(dep)
                if t > best_t:
                    best_t, best_path = t, path
            result = (best_t + step.timeout_sec, best_path + [sid])
            memo[sid] = result
            return result

        terminal_steps = [
            s.id for s in steps
            if not any(s.id in other.depends_on for other in steps)
        ]
        if not terminal_steps:
            return [steps[0].id] if steps else []

        _, cp = max((longest(sid) for sid in terminal_steps), key=lambda x: x[0])
        return cp
