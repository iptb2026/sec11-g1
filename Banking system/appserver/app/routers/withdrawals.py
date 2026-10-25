# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_money
from app.core.money import credit, current_limit, debit, ensure_active, ensure_funds, ensure_minimum_balance, lock_account, reject_money_edits
from app.core.references import resolve_reference
from app.core.security import get_current_user, own_account_ids
from app.core.timeutil import to_philippine_time, utc_now
from app.database.session import get_db
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalOut

router = APIRouter(prefix="/withdrawals", tags=["Layer 4 - Withdrawals"])


@router.post("/", response_model=WithdrawalOut, status_code=status.HTTP_201_CREATED)
def create_withdrawal(withdrawal: WithdrawalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Lock the account row for the duration of this transaction — without
    # this, two withdrawals submitted at nearly the same moment could both
    # read the same starting balance and one of their deductions would be
    # silently lost (a "lost update").
    account = lock_account(db, withdrawal.account_id)

    ensure_active(account, "withdraw")
    ensure_funds(account, withdrawal.amount)
    ensure_minimum_balance(db, account, withdrawal.amount)

    # If this account has a daily withdrawal limit (Layer 3), enforce it.
    # current_limit() locks the row and starts a new day's count when
    # last_reset_date is before today.
    limit = current_limit(db, account)
    if limit and (limit.daily_used_amount + withdrawal.amount) > limit.daily_limit_amount:
        raise HTTPException(status_code=400, detail="This withdrawal would exceed the daily withdrawal limit")

    # The date and who approved it come from the server, never the client.
    now = utc_now()
    withdrawal.reference_number = resolve_reference(db, Withdrawal.reference_number, withdrawal.reference_number, "WD", "reference_number", now)
    new_withdrawal = Withdrawal(**withdrawal.model_dump(), transaction_date=now, approved_by_user_id=current_user.id)
    db.add(new_withdrawal)

    debit(db, account, withdrawal.amount, withdrawal.reference_number, "WITHDRAWAL", now)
    if limit:
        limit.daily_used_amount += withdrawal.amount

    commit_money(db)
    db.refresh(new_withdrawal)
    return new_withdrawal


@router.get("/", response_model=list[WithdrawalOut])
def list_withdrawals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Withdrawal)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see their own accounts' rows
        query = query.filter(Withdrawal.account_id.in_(ids))
    return query.all()


@router.get("/{withdrawal_id}", response_model=WithdrawalOut)
def get_withdrawal(withdrawal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    ids = own_account_ids(current_user, db)
    if not withdrawal or (ids is not None and not withdrawal.account_id in ids):
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return withdrawal


@router.put("/{withdrawal_id}", response_model=WithdrawalOut)
def update_withdrawal(withdrawal_id: int, data: WithdrawalCreate, db: Session = Depends(get_db)):
    """Fixes the descriptive fields only; the amount and the account cannot change (see deposits.py)."""
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    if not (data.reference_number or "").strip():
        data.reference_number = withdrawal.reference_number  # blank keeps the current one
    fields = data.model_dump()
    reject_money_edits(withdrawal, fields, ("account_id", "amount"))

    duplicate = db.query(Withdrawal).filter(
        Withdrawal.reference_number == data.reference_number, Withdrawal.id != withdrawal_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    for field, value in fields.items():
        setattr(withdrawal, field, value)

    db.commit()
    db.refresh(withdrawal)
    return withdrawal


@router.delete("/{withdrawal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_withdrawal(withdrawal_id: int, db: Session = Depends(get_db)):
    """
    Reverses the withdrawal: the amount goes back into the account (ledger
    REVERSAL). If it was made today, it also stops counting toward today's
    withdrawal limit.
    """
    withdrawal = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).with_for_update().first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    account = lock_account(db, withdrawal.account_id)
    credit(db, account, withdrawal.amount, withdrawal.reference_number, "REVERSAL")

    limit = current_limit(db, account)
    if limit and to_philippine_time(withdrawal.transaction_date).date() == limit.last_reset_date:
        limit.daily_used_amount = max(limit.daily_used_amount - withdrawal.amount, 0)

    db.delete(withdrawal)
    commit_money(db)
