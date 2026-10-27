"""
Automatic audit logging.

Every INSERT, UPDATE and DELETE that goes through SQLAlchemy writes an
audit_logs row in the same transaction, so nothing can change without a
record of it and nobody has to remember to log by hand. The logged-in user,
IP and user agent come from session.info, filled in by get_current_user()
(and by /auth/login) for the request's database session.
"""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import event, inspect

from app.database.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.ledger_entry import LedgerEntry
from app.models.session import UserSession
from app.models.user import User

# Never copied into an audit row.
SECRET_COLUMNS = {"hashed_password", "jwt_token", "refresh_token"}
# The ledger is already a log of every balance change; auditing it would
# only double the rows. audit_logs itself is skipped to avoid recursion.
SKIPPED_MODELS = (AuditLog, LedgerEntry)


def remember_request_user(db, user_id, request=None) -> None:
    db.info["audit_user_id"] = user_id
    if request is not None:
        db.info["audit_ip"] = request.client.host if request.client else None
        db.info["audit_user_agent"] = request.headers.get("user-agent")


def _plain(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _columns(obj) -> dict:
    return {
        attr.key: _plain(getattr(obj, attr.key))
        for attr in inspect(obj).mapper.column_attrs
        if attr.key not in SECRET_COLUMNS
    }


def _changes(obj) -> tuple[dict, dict]:
    old, new = {}, {}
    state = inspect(obj)
    for attr in state.mapper.column_attrs:
        history = state.attrs[attr.key].history
        if not history.has_changes() or attr.key in SECRET_COLUMNS:
            if attr.key in SECRET_COLUMNS and history.has_changes():
                old[attr.key] = new[attr.key] = "(changed)"
            continue
        old[attr.key] = _plain(history.deleted[0]) if history.deleted else None
        new[attr.key] = _plain(history.added[0]) if history.added else None
    return old, new


def _action(obj, kind: str, new: dict | None) -> str:
    if isinstance(obj, UserSession):
        if kind == "CREATE":
            return "LOGIN"
        if new and "revoked_at" in new:
            return "LOGOUT"
    return kind


@event.listens_for(SessionLocal, "after_flush")
def write_audit_rows(session, flush_context):
    # after_flush still sees the pre-flush new/dirty/deleted lists and the
    # attribute history, and new rows already have their ids.
    rows = []
    for kind, objects in (("CREATE", session.new), ("UPDATE", session.dirty), ("DELETE", session.deleted)):
        for obj in objects:
            if isinstance(obj, SKIPPED_MODELS) or not hasattr(obj, "__table__"):
                continue
            if kind == "CREATE":
                old, new = None, _columns(obj)
            elif kind == "DELETE":
                old, new = _columns(obj), None
            else:
                old, new = _changes(obj)
                if not new:
                    continue
                # A login only stamps users.last_login_at; the LOGIN row covers it.
                if isinstance(obj, User) and set(new) <= {"last_login_at", "updated_at"}:
                    continue
            rows.append({
                "user_id": session.info.get("audit_user_id"),
                "action_type": _action(obj, kind, new),
                "entity_name": obj.__table__.name,
                "entity_id": getattr(obj, "id", None),
                "old_value": old,
                "new_value": new,
                "ip_address": session.info.get("audit_ip"),
                "user_agent": session.info.get("audit_user_agent"),
            })
    if rows:
        session.connection().execute(AuditLog.__table__.insert(), rows)
