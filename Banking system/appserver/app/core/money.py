"""
Shared rules for every endpoint that moves money.

Each balance change goes through credit()/debit(), which also writes the
matching ledger_entries row, so the ledger is filled automatically and
always agrees with the balances.
"""
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.timeutil import philippine_today, utc_now
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.ledger_entry import LedgerEntry
from app.models.withdrawal_limit import WithdrawalLimit

ZERO = Decimal("0.00")


def lock_account(db: Session, account_id: int, label: str = "account_id") -> Account:
    """
    Load an account and lock its row until the commit, so a second request
    touching the same account waits instead of reading a stale balance.
    """
    account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail=f"{label} does not exist")
    return account


def ensure_active(account: Account, action: str) -> None:
    """Deposits, withdrawals and transfers (both sides) need an ACTIVE account."""
    if account.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Account {account.account_number} is {account.status}, cannot {action}")


def ensure_funds(account: Account, amount: Decimal, what: str = "Insufficient balance") -> None:
    if account.available_balance < amount:
        raise HTTPException(status_code=400, detail=what)


def ensure_minimum_balance(db: Session, account: Account, amount: Decimal) -> None:
    """
    Money the customer sends out (withdrawals, transfers, interbank) may not
    take the balance below the account type's minimum_balance. Reversals and
    fees don't check this: undoing a mistake must always be possible.
    """
    account_type = db.query(AccountType).filter(AccountType.id == account.account_type_id).first()
    minimum = account_type.minimum_balance if account_type else ZERO
    if minimum and account.available_balance - amount < minimum:
        raise HTTPException(
            status_code=400,
            detail=f"Account {account.account_number} must keep a minimum balance of {minimum:,.2f} ({account_type.type_code})",
        )


def _post(db: Session, account: Account, reference: str, kind: str,
          debit: Decimal, credit: Decimal, when: datetime | None) -> None:
    db.add(LedgerEntry(
        account_id=account.id,
        transaction_reference=reference,
        transaction_type=kind,
        debit_amount=debit,
        credit_amount=credit,
        balance_after=account.available_balance,
        transaction_date=when or utc_now(),
    ))


def credit(db: Session, account: Account, amount: Decimal, reference: str, kind: str,
           when: datetime | None = None) -> None:
    """Money enters the account: update both balances and write the ledger row."""
    account.available_balance += amount
    account.ledger_balance += amount
    _post(db, account, reference, kind, ZERO, amount, when)


def debit(db: Session, account: Account, amount: Decimal, reference: str, kind: str,
          when: datetime | None = None) -> None:
    """Money leaves the account: update both balances and write the ledger row."""
    account.available_balance -= amount
    account.ledger_balance -= amount
    _post(db, account, reference, kind, amount, ZERO, when)


def current_limit(db: Session, account: Account) -> WithdrawalLimit | None:
    """
    The account's withdrawal limit row, locked, with daily_used_amount reset
    to 0 when last_reset_date is before today. Without the reset the
    "daily" limit would really be a lifetime limit.
    """
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).with_for_update().first()
    today = philippine_today()  # the day starts at midnight Philippine time
    if limit and limit.last_reset_date < today:
        limit.daily_used_amount = ZERO
        limit.last_reset_date = today
    return limit


def reject_money_edits(record, data: dict, money_fields: tuple[str, ...]) -> None:
    """
    PUT on a posted transaction may only fix descriptive fields (remarks,
    channel...). Changing an amount or an account would leave the balance
    wrong, so it is refused; delete the transaction (which reverses it) and
    record a new one instead.
    """
    changed = [f for f in money_fields if f in data and data[f] != getattr(record, f)]
    if changed:
        raise HTTPException(
            status_code=400,
            detail=f"{', '.join(changed)} cannot be changed on a posted transaction; "
                   "delete it (the balance is reversed) and create a new one",
        )
