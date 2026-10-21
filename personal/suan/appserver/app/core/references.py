"""
Auto-generated transaction reference numbers: PREFIX + MMDDYYYY + 4 random digits.

    DP101020264821   deposit
    WD101020260317   withdrawal
    TR101020269902   internal transfer
    IB101020261150   interbank transfer
"""
import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session


def generate_reference(db: Session, column, prefix: str, when: Optional[datetime] = None) -> str:
    """Returns a reference not yet used in `column` (e.g. Deposit.reference_number)."""
    when = when or datetime.utcnow()
    while True:
        reference = f"{prefix}{when:%m%d%Y}{secrets.randbelow(10000):04d}"
        if not db.query(column).filter(column == reference).first():
            return reference
