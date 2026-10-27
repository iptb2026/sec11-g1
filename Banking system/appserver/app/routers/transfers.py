# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db_utils import commit_money
from app.core.money import credit, debit, ensure_active, ensure_funds, ensure_minimum_balance, reject_money_edits
from app.core.references import resolve_reference
from app.core.security import ADMIN_STAFF, get_current_user, own_account_ids, roles_required
from app.core.timeutil import utc_now
from app.database.session import get_db
from app.models.account import Account
from app.models.transfer import Transfer
from app.models.user import User
from app.schemas.transfer import TransferCreate, TransferOut

router = APIRouter(prefix="/transfers", tags=["Layer 4 - Transfers"])


def lock_both(db: Session, source_id: int, destination_id: int):
    """
    Lock both accounts for the duration of this transaction so a
    simultaneous transfer touching either one can't read a stale balance.
    Locking order matters: always lock the lower id first, or two transfers
    running in opposite directions at the same time (A->B and B->A) could
    each be waiting on the row the other one is holding — a deadlock.
    """
    first_id, second_id = sorted([source_id, destination_id])
    accounts_by_id = {
        a.id: a
        for a in db.query(Account).filter(Account.id.in_([first_id, second_id])).with_for_update().all()
    }
    return accounts_by_id.get(source_id), accounts_by_id.get(destination_id)


@router.post("/", response_model=TransferOut, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Staff move money between any accounts. A customer (Send Money) may only
    send from one of their own accounts, to any active account by number.
    """
    if transfer.destination_account_id is None:
        number = transfer.destination_account_number.strip()
        destination_row = db.query(Account.id).filter(Account.account_number == number).first()
        if not destination_row:
            raise HTTPException(status_code=400, detail=f"No account with number {number}")
        transfer.destination_account_id = destination_row.id

    own_ids = own_account_ids(current_user, db)  # None for staff, the customer's own ids otherwise
    if own_ids is not None and transfer.source_account_id not in own_ids:
        raise HTTPException(status_code=403, detail="You can only send money from your own accounts")

    if transfer.source_account_id == transfer.destination_account_id:
        raise HTTPException(status_code=400, detail="source and destination accounts must be different")

    source, destination = lock_both(db, transfer.source_account_id, transfer.destination_account_id)
    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")
    if not destination:
        raise HTTPException(status_code=400, detail="destination_account_id does not exist")

    # Both sides must be ACTIVE: money can't leave a frozen/closed account
    # or be sent into one.
    ensure_active(source, "send transfers")
    ensure_active(destination, "receive transfers")
    ensure_funds(source, transfer.amount)
    ensure_minimum_balance(db, source, transfer.amount)

    now = utc_now()
    transfer.transfer_reference = resolve_reference(db, Transfer.transfer_reference, transfer.transfer_reference, "TR", "transfer_reference", now)
    new_transfer = Transfer(**transfer.model_dump(exclude={"destination_account_number"}), status="SUCCESS", completed_at=now)
    db.add(new_transfer)

    # Move the money: debit source, credit destination — both accounts,
    # same request, same commit, one ledger row on each side.
    debit(db, source, transfer.amount, transfer.transfer_reference, "TRANSFER_DEBIT", now)
    credit(db, destination, transfer.amount, transfer.transfer_reference, "TRANSFER_CREDIT", now)

    commit_money(db)
    db.refresh(new_transfer)
    return new_transfer


@router.get("/", response_model=list[TransferOut])
def list_transfers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Transfer)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see their own accounts' rows
        query = query.filter(or_(Transfer.source_account_id.in_(ids), Transfer.destination_account_id.in_(ids)))
    return query.all()


@router.get("/{transfer_id}", response_model=TransferOut)
def get_transfer(transfer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    ids = own_account_ids(current_user, db)
    if not transfer or (ids is not None and not (transfer.source_account_id in ids or transfer.destination_account_id in ids)):
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.put("/{transfer_id}", response_model=TransferOut, dependencies=[roles_required(ADMIN_STAFF)])
def update_transfer(transfer_id: int, data: TransferCreate, db: Session = Depends(get_db)):
    """Fixes the descriptive fields only; the amount and the accounts cannot change (see deposits.py)."""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    if not (data.transfer_reference or "").strip():
        data.transfer_reference = transfer.transfer_reference  # blank keeps the current one
    fields = data.model_dump(exclude={"destination_account_number"})
    reject_money_edits(transfer, fields, ("source_account_id", "destination_account_id", "amount"))

    duplicate = db.query(Transfer).filter(
        Transfer.transfer_reference == data.transfer_reference, Transfer.id != transfer_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="transfer_reference already exists")

    for field, value in fields.items():
        setattr(transfer, field, value)

    db.commit()
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[roles_required(ADMIN_STAFF)])
def delete_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """Reverses the transfer: the amount moves back from the destination to the source (ledger REVERSAL on both)."""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).with_for_update().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    source, destination = lock_both(db, transfer.source_account_id, transfer.destination_account_id)
    if not source or not destination:
        raise HTTPException(status_code=400, detail="One of the accounts no longer exists, cannot reverse")
    ensure_funds(destination, transfer.amount, "The destination account no longer holds this amount, cannot reverse")

    debit(db, destination, transfer.amount, transfer.transfer_reference, "REVERSAL")
    credit(db, source, transfer.amount, transfer.transfer_reference, "REVERSAL")

    db.delete(transfer)
    commit_money(db)
