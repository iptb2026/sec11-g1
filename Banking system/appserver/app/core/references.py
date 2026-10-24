"""
Auto-generated transaction reference numbers: PREFIX + MMDDYYYY + 4 random digits.

    DP102420264821   deposit
    WD102420260317   withdrawal
    TR102420269902   internal transfer
    IB102420261150   interbank transfer

Staff can still type their own reference; a blank one is generated here.
"""
import secrets
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.timeutil import utc_now


def generate_reference(db: Session, column, prefix: str, when: Optional[datetime] = None) -> str:
    """Returns a reference not yet used in `column` (e.g. Deposit.reference_number)."""
    when = when or utc_now()
    while True:
        reference = f"{prefix}{when:%m%d%Y}{secrets.randbelow(10000):04d}"
        if not db.query(column).filter(column == reference).first():
            return reference


def resolve_reference(db: Session, column, typed: Optional[str], prefix: str, field: str, when: Optional[datetime] = None) -> str:
    """
    The reference for a new transaction: the typed one if it is unused,
    otherwise a generated one when nothing was typed.
    """
    typed = (typed or "").strip()
    if not typed:
        return generate_reference(db, column, prefix, when)
    if db.query(column).filter(column == typed).first():
        raise HTTPException(status_code=400, detail=f"{field} already exists")
    return typed
