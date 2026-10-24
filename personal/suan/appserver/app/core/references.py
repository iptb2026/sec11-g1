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


ACCOUNT_NUMBER_BASE = 1000000000


def account_number_for(account_id: int) -> str:
    """
    The account number for a new account: 1000000000 + its database id
    (id 15 -> "1000000015"). MySQL hands out every id exactly once, so two
    accounts opened at the same moment can never get the same number.
    """
    return str(ACCOUNT_NUMBER_BASE + account_id)


def generate_reference(db: Session, column, prefix: str, when: Optional[datetime] = None) -> str:
    """Returns a reference not yet used in `column` (e.g. Deposit.reference_number)."""
    when = when or datetime.utcnow()
    while True:
        reference = f"{prefix}{when:%m%d%Y}{secrets.randbelow(10000):04d}"
        if not db.query(column).filter(column == reference).first():
            return reference
