# ==== LAYER 5: Financial Records & Ledger ====
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_money
from app.core.money import credit, debit, lock_account, reject_money_edits
from app.core.security import get_current_user, own_account_ids
from app.database.session import get_db
from app.models.deposit import Deposit
from app.models.fee_record import FeeRecord
from app.models.fee_type import FeeType
from app.models.interbank_transfer import InterbankTransfer
from app.models.transfer import Transfer
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.schemas.fee_record import FeeRecordCreate, FeeRecordOut

router = APIRouter(prefix="/fee-records", tags=["Layer 5 - Fee Records"])

CENT = Decimal("0.01")


def transaction_amount(db: Session, reference: str) -> Decimal | None:
    """The amount of the deposit/withdrawal/transfer/interbank transfer with this reference."""
    for model, column in (
        (Deposit, Deposit.reference_number),
        (Withdrawal, Withdrawal.reference_number),
        (Transfer, Transfer.transfer_reference),
        (InterbankTransfer, InterbankTransfer.reference_number),
    ):
        row = db.query(model).filter(column == reference).first()
        if row:
            return row.amount
    return None


def calculate_fee(db: Session, fee_type: FeeType, reference: str | None) -> Decimal:
    """
    fee = fixed_amount + percentage_rate % of the transaction it is charged on.
    A percentage fee needs transaction_reference to know what to take the
    percentage of. Computed here, never taken from the client.
    """
    fee = Decimal(fee_type.fixed_amount or 0)
    rate = Decimal(fee_type.percentage_rate or 0)
    if rate:
        if not reference:
            raise HTTPException(status_code=400, detail=f"{fee_type.fee_code} is a percentage fee; transaction_reference is required")
        base = transaction_amount(db, reference)
        if base is None:
            raise HTTPException(status_code=400, detail="transaction_reference does not match any transaction")
        fee += base * rate / 100
    fee = fee.quantize(CENT, rounding=ROUND_HALF_UP)
    if fee <= 0:
        raise HTTPException(status_code=400, detail=f"Fee type {fee_type.fee_code} charges nothing (fixed amount and rate are 0)")
    return fee


@router.post("/", response_model=FeeRecordOut, status_code=status.HTTP_201_CREATED)
def create_fee_record(fee: FeeRecordCreate, db: Session = Depends(get_db)):
    # Lock the account row — see the same note in deposits.py / withdrawals.py.
    account = lock_account(db, fee.account_id)
    if account.status == "CLOSED":
        raise HTTPException(status_code=400, detail="Account is CLOSED, cannot charge a fee")

    fee_type = db.query(FeeType).filter(FeeType.id == fee.fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=400, detail="fee_type_id does not exist")

    # Any amount_charged sent by the client is ignored.
    amount = calculate_fee(db, fee_type, fee.transaction_reference)
    new_fee = FeeRecord(**fee.model_dump(exclude={"amount_charged"}), amount_charged=amount)
    db.add(new_fee)
    db.flush()  # gives new_fee its id, used as the ledger reference below

    # Unlike a withdrawal, a fee is allowed to push the balance negative —
    # banks charge maintenance/overdraft fees regardless of available funds.
    debit(db, account, amount, fee.transaction_reference or f"FEE-{new_fee.id}", "FEE")

    commit_money(db)
    db.refresh(new_fee)
    return new_fee


@router.get("/", response_model=list[FeeRecordOut])
def list_fee_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(FeeRecord)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see fees on their own accounts
        query = query.filter(FeeRecord.account_id.in_(ids))
    return query.all()


@router.get("/{fee_id}", response_model=FeeRecordOut)
def get_fee_record(fee_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fee = db.query(FeeRecord).filter(FeeRecord.id == fee_id).first()
    ids = own_account_ids(current_user, db)
    if not fee or (ids is not None and not fee.account_id in ids):
        raise HTTPException(status_code=404, detail="Fee record not found")
    return fee


@router.put("/{fee_id}", response_model=FeeRecordOut)
def update_fee_record(fee_id: int, data: FeeRecordCreate, db: Session = Depends(get_db)):
    """Fixes remarks only. The account, fee type and transaction decide the amount, so they cannot change."""
    fee = db.query(FeeRecord).filter(FeeRecord.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")

    fields = data.model_dump(exclude={"amount_charged"})
    reject_money_edits(fee, fields, ("account_id", "fee_type_id", "transaction_reference"))
    fee.remarks = data.remarks

    db.commit()
    db.refresh(fee)
    return fee


@router.delete("/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_record(fee_id: int, db: Session = Depends(get_db)):
    """Reverses the fee: the amount goes back into the account (ledger REVERSAL)."""
    fee = db.query(FeeRecord).filter(FeeRecord.id == fee_id).with_for_update().first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")

    account = lock_account(db, fee.account_id)
    credit(db, account, fee.amount_charged, fee.transaction_reference or f"FEE-{fee.id}", "REVERSAL")

    db.delete(fee)
    commit_money(db)
