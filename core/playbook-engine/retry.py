"""
Retry Engine — executes a callable with configurable backoff and circuit breaker.

Supports: fixed | linear | exponential | jitter backoff
Circuit breaker: trips after N consecutive failures, resets after cooldown.
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine

from playbooks.schema.playbook_schema import BackoffStrategy, RetryPolicy

logger = logging.getLogger("arizen.playbook.retry")


class RetryOutcome(str, Enum):
    SUCCESS       = "success"
    EXHAUSTED     = "exhausted"    # all retries failed
    NOT_RETRYABLE = "not_retryable"  # error type excluded from retry
    CIRCUIT_OPEN  = "circuit_open"   # circuit breaker tripped


@dataclass
class RetryResult:
    outcome:    RetryOutcome
    attempts:   int     = 0
    last_error: str     = ""
    result:     Any     = None
    total_sec:  float   = 0.0


@dataclass
class CircuitBreakerState:
    failures:      int   = 0
    tripped_at:    float = 0.0
    cooldown_sec:  float = 60.0
    trip_threshold: int  = 5

    @property
    def is_open(self) -> bool:
        if self.failures < self.trip_threshold:
            return False
        elapsed = time.monotonic() - self.tripped_at
        return elapsed < self.cooldown_sec

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.trip_threshold:
            self.tripped_at = time.monotonic()

    def record_success(self) -> None:
        self.failures = 0


# Global circuit breakers per (agent, tool) pair
_CIRCUIT_BREAKERS: dict[str, CircuitBreakerState] = {}


def _get_breaker(key: str) -> CircuitBreakerState:
    if key not in _CIRCUIT_BREAKERS:
        _CIRCUIT_BREAKERS[key] = CircuitBreakerState()
    return _CIRCUIT_BREAKERS[key]


class RetryEngine:
    """
    Executes an async callable with the given RetryPolicy.

    Usage:
        engine = RetryEngine()
        result = await engine.run(
            fn=my_async_fn,
            args=(arg1, arg2),
            policy=step.retry,
            circuit_key="coder:code.generate",
        )
    """

    async def run(
        self,
        fn:          Callable[..., Coroutine],
        args:        tuple    = (),
        kwargs:      dict     = None,
        policy:      RetryPolicy = None,
        circuit_key: str     = "",
    ) -> RetryResult:
        if policy is None:
            policy = RetryPolicy(max_attempts=1)
        kwargs = kwargs or {}

        breaker = _get_breaker(circuit_key) if circuit_key else None
        if breaker and breaker.is_open:
            logger.warning("Circuit breaker OPEN for %s — skipping execution", circuit_key)
            return RetryResult(outcome=RetryOutcome.CIRCUIT_OPEN)

        start    = time.monotonic()
        attempts = 0
        last_err = ""

        for attempt in range(1, policy.max_attempts + 1):
            attempts = attempt
            try:
                result = await fn(*args, **kwargs)
                if breaker:
                    breaker.record_success()
                return RetryResult(
                    outcome=RetryOutcome.SUCCESS,
                    attempts=attempts,
                    result=result,
                    total_sec=time.monotonic() - start,
                )
            except Exception as exc:
                last_err  = str(exc)
                exc_type  = type(exc).__name__.lower()

                # Check if this error type is excluded from retry
                not_retryable = any(excl.lower() in exc_type for excl in policy.not_on)
                if not_retryable:
                    logger.info("Error '%s' is not retryable per policy", exc_type)
                    if breaker:
                        breaker.record_failure()
                    return RetryResult(
                        outcome=RetryOutcome.NOT_RETRYABLE,
                        attempts=attempts,
                        last_error=last_err,
                        total_sec=time.monotonic() - start,
                    )

                # Check if this error type is in the retry list
                retryable = any(r.lower() in exc_type or r.lower() in last_err.lower()
                                for r in policy.on)
                if not retryable:
                    retryable = True  # default to retry unless specifically excluded

                if attempt < policy.max_attempts and retryable:
                    delay = self._backoff(policy, attempt)
                    logger.warning(
                        "Attempt %d/%d failed: %s. Retrying in %.1fs",
                        attempt, policy.max_attempts, last_err[:100], delay
                    )
                    await asyncio.sleep(delay)
                else:
                    if breaker:
                        breaker.record_failure()

        return RetryResult(
            outcome=RetryOutcome.EXHAUSTED,
            attempts=attempts,
            last_error=last_err,
            total_sec=time.monotonic() - start,
        )

    def _backoff(self, policy: RetryPolicy, attempt: int) -> float:
        base = policy.delay_sec
        match policy.backoff:
            case BackoffStrategy.FIXED:
                delay = base
            case BackoffStrategy.LINEAR:
                delay = base * attempt
            case BackoffStrategy.EXPONENTIAL:
                delay = base * (2 ** (attempt - 1))
            case BackoffStrategy.JITTER:
                delay = base * (2 ** (attempt - 1)) * (0.5 + random.random() * 0.5)
            case _:
                delay = base
        return min(delay, policy.max_delay_sec)
