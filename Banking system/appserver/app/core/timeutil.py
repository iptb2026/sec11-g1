from datetime import datetime, timedelta, timezone

# Philippine time is always UTC+8 (no daylight saving), so a fixed offset is
# exact and needs no time-zone database on the server.
PHILIPPINE_TIME = timezone(timedelta(hours=8), "PHT")


def utc_now() -> datetime:
    """
    The current time in UTC, without tzinfo.

    Replaces the deprecated datetime.utcnow(). The tzinfo is dropped on
    purpose: MySQL DATETIME columns store naive values, so every datetime
    read back from the database is naive, and comparing a naive one with
    an aware one raises TypeError.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_philippine_time(utc_naive: datetime) -> datetime:
    """A naive UTC datetime (as stored in MySQL) in Philippine time, still naive."""
    return utc_naive.replace(tzinfo=timezone.utc).astimezone(PHILIPPINE_TIME).replace(tzinfo=None)


def philippine_today():
    """Today's date in the Philippines: the bank's "day" for daily limits and policies."""
    return to_philippine_time(utc_now()).date()
