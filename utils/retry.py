from __future__ import annotations

import time
from functools import wraps
from typing import Callable, TypeVar, Any

F = TypeVar("F", bound=Callable[..., Any])


def is_transient_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "429", "503", "502", "504", "timeout", "timed out",
        "tempor", "connection", "unavailable", "resource_exhausted",
        "rate limit", "overloaded"
    )
    return any(marker in text for marker in markers)


def retry_call(func: Callable[[], Any], *, max_attempts: int = 4, delay: int = 5):
    """Execute a zero-argument callable with retries for transient failures."""
    last = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as exc:
            last = exc
            if not is_transient_error(exc) or attempt >= max_attempts:
                raise
            time.sleep(delay)
    raise last


def retry_transient(_func: F | None = None, *, max_attempts: int = 4, delay: int = 5):
    """Decorator form for functions that need automatic transient-error retries."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_call(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                delay=delay,
            )
        return wrapper  # type: ignore[return-value]

    if _func is not None:
        return decorator(_func)
    return decorator
