# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_money
from app.core.money import credit, debit, ensure_active, ensure_funds, lock_account, reject_money_edits
from app.core.security import get_current_user, own_account_ids
from app.database.session import get_db
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"])


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db)):
    # lock_account() locks this account row until the commit below, so a
    # second request touching the same account has to wait its turn instead
    # of reading a stale balance and silently overwriting this change.
    account = lock_account(db, deposit.account_id)

    if deposit.deposited_by_user_id is not None:
        user = db.query(User).filter(User.id == deposit.deposited_by_user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="deposited_by_user_id does not exist")

    existing = db.query(Deposit).filter(Deposit.reference_number == deposit.reference_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    # FROZEN and CLOSED accounts cannot receive deposits.
    ensure_active(account, "receive deposits")

    new_deposit = Deposit(**deposit.model_dump())
    db.add(new_deposit)

    # This is the actual point of a deposit: money enters the account.
    credit(db, account, deposit.amount, deposit.reference_number, "DEPOSIT", deposit.transaction_date)

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


@router.put("/{deposit_id}", response_model=DepositOut)
def update_deposit(deposit_id: int, data: DepositCreate, db: Session = Depends(get_db)):
    """
    Fixes the descriptive fields only (remarks, channel, date...). The amount
    and the account cannot change: that would leave the balance wrong. Delete
    the deposit instead (which reverses it) and record a new one.
    """
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

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
    """Reverses the deposit: the amount leaves the account again, and the ledger records a REVERSAL."""
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).with_for_update().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    account = lock_account(db, deposit.account_id)
    ensure_funds(account, deposit.amount, "The account no longer holds this deposit's amount, cannot reverse it")
    debit(db, account, deposit.amount, deposit.reference_number, "REVERSAL")

    db.delete(deposit)
    commit_money(db)
