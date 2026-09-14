import time
from functools import wraps

def retry_transient(func, attempts=4, delay=5):
    last = None
    for attempt in range(attempts):
        try: return func()
        except Exception as exc:
            last = exc
            text = str(exc).lower()
            retryable = any(x in text for x in ["429", "503", "timeout", "tempor", "connection", "unavailable", "resource_exhausted"])
            if not retryable or attempt == attempts - 1: raise
            time.sleep(delay)
    raise last
