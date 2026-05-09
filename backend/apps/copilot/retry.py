"""
Retry utility for AI provider calls with timeout handling.

Retries failed API calls up to AI_RETRY_ATTEMPTS times with AI_RETRY_DELAY_SECONDS
between each attempt. If all retries fail and a fallback provider is configured,
the fallback is used instead.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, TypeVar

from django.conf import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AIProviderTimeoutError(Exception):
    """Raised when an AI provider request times out after retries."""
    pass


class AIProviderError(Exception):
    """Raised when an AI provider request fails after retries."""

    def __init__(self, message: str, last_error: Exception | None = None):
        super().__init__(message)
        self.last_error = last_error


def retry_ai_call(
    fn: Callable[[], T],
    *,
    max_retries: int | None = None,
    delay_seconds: float | None = None,
    operation_name: str = "AI provider call",
) -> T:
    """
    Execute an AI provider call with retry logic.

    Args:
        fn: The callable to execute (should make the AI API call)
        max_retries: Number of retry attempts (default from settings.AI_RETRY_ATTEMPTS)
        delay_seconds: Delay between retries (default from settings.AI_RETRY_DELAY_SECONDS)
        operation_name: Name for logging purposes

    Returns:
        The result of the successful call

    Raises:
        AIProviderError: If all retries are exhausted
        AIProviderTimeoutError: If all retries time out
    """
    if max_retries is None:
        max_retries = int(getattr(settings, "AI_RETRY_ATTEMPTS", 2))
    if delay_seconds is None:
        delay_seconds = float(getattr(settings, "AI_RETRY_DELAY_SECONDS", 2))

    last_error: Exception | None = None
    total_attempts = 1 + max_retries  # initial attempt + retries

    for attempt in range(1, total_attempts + 1):
        try:
            logger.debug("%s: attempt %d/%d", operation_name, attempt, total_attempts)
            result = fn()
            if attempt > 1:
                logger.info("%s: succeeded on attempt %d/%d", operation_name, attempt, total_attempts)
            return result
        except Exception as exc:
            last_error = exc
            is_timeout = "timeout" in str(exc).lower() or "timed out" in str(exc).lower()
            is_rate_limit = "429" in str(exc) or "rate" in str(exc).lower()

            if attempt < total_attempts:
                wait = delay_seconds * attempt  # exponential-ish backoff
                logger.warning(
                    "%s: attempt %d/%d failed (%s), retrying in %.1fs...",
                    operation_name, attempt, total_attempts,
                    type(exc).__name__, wait,
                )
                time.sleep(wait)
            else:
                if is_timeout:
                    raise AIProviderTimeoutError(
                        f"{operation_name} timed out after {total_attempts} attempts."
                    ) from exc
                raise AIProviderError(
                    f"{operation_name} failed after {total_attempts} attempts: {exc}",
                    last_error=exc,
                ) from exc

    # Should not reach here, but just in case
    raise AIProviderError(f"{operation_name} failed unexpectedly.", last_error=last_error)
