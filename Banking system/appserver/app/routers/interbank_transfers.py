# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_money
from app.core.money import credit, debit, ensure_active, ensure_funds, lock_account
from app.core.security import get_current_user, own_account_ids
from app.core.timeutil import utc_now
from app.database.session import get_db
from app.models.bank import Bank
from app.models.interbank_transfer import InterbankTransfer
from app.models.user import User
from app.schemas.interbank_transfer import (
    InterbankTransferCreate,
    InterbankTransferStatusUpdate,
    InterbankTransferOut,
)

router = APIRouter(prefix="/interbank-transfers", tags=["Layer 4 - Interbank Transfers"])

# These statuses mean the money was returned to the source account.
REFUNDED_STATUSES = ("FAILED", "REVERSED")


def refund_to_source(db: Session, transfer: InterbankTransfer) -> None:
    """Return amount + fee to the source account, with a REVERSAL ledger row."""
    source = lock_account(db, transfer.source_account_id, "Source account")
    # Refunded even if the account was frozen/closed since — it is the customer's money.
    refund = transfer.amount + (transfer.transfer_fee or 0)
    credit(db, source, refund, transfer.reference_number, "REVERSAL")


@router.post("/", response_model=InterbankTransferOut, status_code=status.HTTP_201_CREATED)
def create_interbank_transfer(transfer: InterbankTransferCreate, db: Session = Depends(get_db)):
    # Lock the source account row for the duration of this transaction — see
    # the same note in deposits.py / withdrawals.py.
    source = lock_account(db, transfer.source_account_id, "source_account_id")

    bank = db.query(Bank).filter(Bank.id == transfer.target_bank_id).first()
    if not bank:
        raise HTTPException(status_code=400, detail="target_bank_id does not exist")

    existing = db.query(InterbankTransfer).filter(
        InterbankTransfer.reference_number == transfer.reference_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    ensure_active(source, "send transfers")

    total_debit = transfer.amount + transfer.transfer_fee
    ensure_funds(source, total_debit, "Insufficient balance to cover amount + transfer fee")

    # Unlike an internal `transfer`, the destination bank is external — we
    # can only debit our own side. The transfer starts PROCESSING (not
    # SUCCESS) because settlement with the other bank isn't instant; use
    # PUT /interbank-transfers/{id}/status to move it to SUCCESS/FAILED later.
    new_transfer = InterbankTransfer(**transfer.model_dump(), status="PROCESSING")
    db.add(new_transfer)

    debit(db, source, total_debit, transfer.reference_number, "INTERBANK_DEBIT")

    commit_money(db)
    db.refresh(new_transfer)
    return new_transfer


@router.get("/", response_model=list[InterbankTransferOut])
def list_interbank_transfers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(InterbankTransfer)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see their own accounts' rows
        query = query.filter(InterbankTransfer.source_account_id.in_(ids))
    return query.all()


@router.get("/{transfer_id}", response_model=InterbankTransferOut)
def get_interbank_transfer(transfer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).first()
    ids = own_account_ids(current_user, db)
    if not transfer or (ids is not None and not transfer.source_account_id in ids):
        raise HTTPException(status_code=404, detail="Interbank transfer not found")
    return transfer


@router.put("/{transfer_id}/status", response_model=InterbankTransferOut)
def update_interbank_transfer_status(
    transfer_id: int, data: InterbankTransferStatusUpdate, db: Session = Depends(get_db)
):
    """
    Moves a PROCESSING transfer to its final settlement status (SUCCESS/FAILED/REVERSED).

    FAILED and REVERSED mean the money never reached (or came back from) the
    other bank, so amount + transfer_fee is returned to the source account.
    Those two statuses are final: changing them again could refund twice.
    """
    # Lock the transfer row so two simultaneous status changes can't both refund.
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).with_for_update().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    if transfer.status in REFUNDED_STATUSES:
        if data.status == transfer.status:
            return transfer
        raise HTTPException(
            status_code=400,
            detail=f"Transfer is already {transfer.status} and was refunded; its status can no longer change",
        )

    if data.status in REFUNDED_STATUSES:
        refund_to_source(db, transfer)

    transfer.status = data.status
    if data.status in ("SUCCESS", "FAILED", "REVERSED"):
        transfer.completed_at = utc_now()

    commit_money(db)
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interbank_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """
    Reverses the transfer: amount + fee go back to the source account, unless
    it was already refunded (FAILED/REVERSED), so deleting never loses money.
    """
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).with_for_update().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    if transfer.status not in REFUNDED_STATUSES:
        refund_to_source(db, transfer)

    db.delete(transfer)
    commit_money(db)