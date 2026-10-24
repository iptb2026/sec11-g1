from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    The current time in UTC, without tzinfo.

    Replaces the deprecated datetime.utcnow(). The tzinfo is dropped on
    purpose: MySQL DATETIME columns store naive values, so every datetime
    read back from the database is naive, and comparing a naive one with
    an aware one raises TypeError.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
