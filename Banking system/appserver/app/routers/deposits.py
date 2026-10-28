# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db_utils import commit_money
from app.core.money import credit, debit, ensure_active, ensure_funds, lock_account, reject_money_edits
from app.core.references import resolve_reference
from app.core.security import ADMIN_ONLY, get_current_user, own_account_ids, role_code_of, roles_required
from app.core.timeutil import utc_now
from app.database.session import get_db
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"])


def needs_approval(deposit: DepositCreate, user: User, db: Session) -> bool:
    """
    Maker-checker: a large deposit recorded by staff waits for an admin, so
    one teller alone can't put a big balance into an account (for example
    their own customer account) without cash behind it. An admin is the
    checker, so their deposits post straight away.
    """
    return deposit.amount >= settings.LARGE_DEPOSIT_THRESHOLD and role_code_of(user, db) != "ADMIN"


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # lock_account() locks this account row until the commit below, so a
    # second request touching the same account has to wait its turn instead
    # of reading a stale balance and silently overwriting this change.
    account = lock_account(db, deposit.account_id)

    # FROZEN and CLOSED accounts cannot receive deposits.
    ensure_active(account, "receive deposits")

    # The date and who recorded it come from the server, never the client.
    now = utc_now()
    deposit.reference_number = resolve_reference(db, Deposit.reference_number, deposit.reference_number, "DP", "reference_number", now)
    pending = needs_approval(deposit, current_user, db)
    new_deposit = Deposit(
        **deposit.model_dump(),
        transaction_date=now,
        deposited_by_user_id=current_user.id,
        status="PENDING" if pending else "COMPLETED",
    )
    db.add(new_deposit)

    # This is the actual point of a deposit: money enters the account.
    # A pending one only moves money once an admin approves it.
    if not pending:
        credit(db, account, deposit.amount, deposit.reference_number, "DEPOSIT", now)

    commit_money(db)
    db.refresh(new_deposit)
    return new_deposit


@router.get("/", response_model=list[DepositOut])
def list_deposits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Deposit)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see their own accounts' rows
        query = query.filter(Deposit.account_id.in_(ids))
    return query.all()


@router.get("/{deposit_id}", response_model=DepositOut)
def get_deposit(deposit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    ids = own_account_ids(current_user, db)
    if not deposit or (ids is not None and not deposit.account_id in ids):
        raise HTTPException(status_code=404, detail="Deposit not found")
    return deposit


def pending_deposit(db: Session, deposit_id: int, reviewer: User) -> Deposit:
    """The deposit to approve or reject: it must be PENDING and not the reviewer's own."""
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).with_for_update().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    if deposit.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"This deposit is already {deposit.status}")
    if deposit.deposited_by_user_id == reviewer.id:
        raise HTTPException(status_code=403, detail="You cannot approve or reject a deposit you recorded")
    return deposit


@router.post("/{deposit_id}/approve", response_model=DepositOut, dependencies=[roles_required(ADMIN_ONLY)])
def approve_deposit(deposit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """An admin confirms a large deposit: the money enters the account now."""
    deposit = pending_deposit(db, deposit_id, current_user)
    account = lock_account(db, deposit.account_id)
    ensure_active(account, "receive deposits")

    now = utc_now()
    credit(db, account, deposit.amount, deposit.reference_number, "DEPOSIT", now)
    deposit.status = "COMPLETED"
    deposit.reviewed_by_user_id = current_user.id
    deposit.reviewed_at = now

    commit_money(db)
    db.refresh(deposit)
    return deposit


@router.post("/{deposit_id}/reject", response_model=DepositOut, dependencies=[roles_required(ADMIN_ONLY)])
def reject_deposit(deposit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """An admin turns a large deposit down: no money moves, and the row stays as a record."""
    deposit = pending_deposit(db, deposit_id, current_user)
    deposit.status = "REJECTED"
    deposit.reviewed_by_user_id = current_user.id
    deposit.reviewed_at = utc_now()

    db.commit()
    db.refresh(deposit)
    return deposit


@router.put("/{deposit_id}", response_model=DepositOut)
def update_deposit(deposit_id: int, data: DepositCreate, db: Session = Depends(get_db)):
    """
    Fixes the descriptive fields only (reference, channel, remarks). The amount
    and the account cannot change: that would leave the balance wrong. Delete
    the deposit instead (which reverses it) and record a new one.
    """
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    if not (data.reference_number or "").strip():
        data.reference_number = deposit.reference_number  # blank keeps the current one
    fields = data.model_dump()
    reject_money_edits(deposit, fields, ("account_id", "amount"))

    duplicate = db.query(Deposit).filter(
        Deposit.reference_number == data.reference_number, Deposit.id != deposit_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    for field, value in fields.items():
        setattr(deposit, field, value)

    db.commit()
    db.refresh(deposit)
    return deposit


@router.delete("/{deposit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deposit(deposit_id: int, db: Session = Depends(get_db)):
    """
    Reverses the deposit: the amount leaves the account again, and the ledger
    records a REVERSAL. A PENDING or REJECTED deposit never moved money, so
    it is just removed.
    """
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).with_for_update().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    if deposit.status == "COMPLETED":
        account = lock_account(db, deposit.account_id)
        ensure_funds(account, deposit.amount, "The account no longer holds this deposit's amount, cannot reverse it")
        debit(db, account, deposit.amount, deposit.reference_number, "REVERSAL")

    db.delete(deposit)
    commit_money(db)
