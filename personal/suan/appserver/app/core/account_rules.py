"""
Shared business rules that tie an account's money movements back to the
rules defined on its account type (Layer 1) and its withdrawal limit (Layer 3).

Every endpoint that moves money calls these instead of re-implementing the
checks, so the rules can't drift apart between deposits, withdrawals,
transfers, interbank transfers, fees, and interest.
"""
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.account_type import AccountType
from app.models.withdrawal_limit import WithdrawalLimit


def get_account_type(db: Session, account: Account) -> AccountType:
    return db.query(AccountType).filter(AccountType.id == account.account_type_id).first()


def ensure_can_credit(account: Account, label: str = "Account"):
    """Money may enter ACTIVE or FROZEN accounts, never CLOSED ones."""
    if account.status == "CLOSED":
        raise HTTPException(status_code=400, detail=f"{label} is CLOSED, cannot receive funds")


def ensure_can_debit(db: Session, account: Account, amount: Decimal, label: str = "Account"):
    """
    Money may only leave an ACTIVE account, and never below the account
    type's minimum_balance.
    """
    if account.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"{label} is {account.status}, cannot debit")

    if account.available_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account_type = get_account_type(db, account)
    minimum = account_type.minimum_balance if account_type else Decimal("0.00")
    if account.available_balance - amount < minimum:
        raise HTTPException(
            status_code=400,
            detail=f"This would bring the balance below the account type's minimum balance of {minimum}",
        )


def get_or_create_withdrawal_limit(db: Session, account: Account, lock: bool = False):
    """
    Returns the account's withdrawal_limits row, creating it from the account
    type's daily_withdrawal_limit if it's missing (0 on the type = no limit).
    Resets daily_used_amount when the last reset was on an earlier day.
    """
    query = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id)
    if lock:
        query = query.with_for_update()
    limit = query.first()

    if not limit:
        account_type = get_account_type(db, account)
        if not account_type or not account_type.daily_withdrawal_limit:
            return None
        limit = WithdrawalLimit(
            account_id=account.id,
            daily_limit_amount=account_type.daily_withdrawal_limit,
            daily_used_amount=Decimal("0.00"),
            last_reset_date=date.today(),
        )
        db.add(limit)
        db.flush()

    if limit.last_reset_date < date.today():
        limit.daily_used_amount = Decimal("0.00")
        limit.last_reset_date = date.today()

    return limit
