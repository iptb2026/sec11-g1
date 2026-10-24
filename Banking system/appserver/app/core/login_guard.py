"""
Brute-force protection for POST /auth/login.

After MAX_FAILURES wrong passwords in a row for one username, that username
is blocked for LOCK_MINUTES (even with the right password). A successful
login resets the count.

The counts live in this process's memory, not in the database: no schema
change is needed, and restarting the backend clears every block (handy if
someone locks themselves out right before a demo).
"""
import threading
from datetime import datetime, timedelta

from fastapi import HTTPException, status

from app.core.timeutil import utc_now

MAX_FAILURES = 5
LOCK_MINUTES = 15

_lock = threading.Lock()
_failures: dict[str, int] = {}
_blocked_until: dict[str, datetime] = {}


def _key(username: str) -> str:
    return (username or "").strip().lower()


def check_not_blocked(username: str) -> None:
    """Stops the login with 429 while this username is blocked."""
    with _lock:
        until = _blocked_until.get(_key(username))
        if until and until > utc_now():
            minutes = max(1, int((until - utc_now()).total_seconds() // 60) + 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed logins. Try again in {minutes} minute{'s' if minutes != 1 else ''}.",
            )


def record_failure(username: str) -> None:
    with _lock:
        key = _key(username)
        _failures[key] = _failures.get(key, 0) + 1
        if _failures[key] >= MAX_FAILURES:
            _blocked_until[key] = utc_now() + timedelta(minutes=LOCK_MINUTES)
            _failures[key] = 0


def record_success(username: str) -> None:
    with _lock:
        key = _key(username)
        _failures.pop(key, None)
        _blocked_until.pop(key, None)
