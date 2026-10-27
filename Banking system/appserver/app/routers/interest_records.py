# ==== LAYER 5: Financial Records & Ledger ====
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_money
from app.core.money import credit, debit, lock_account
from app.core.security import get_current_user, own_account_ids
from app.core.timeutil import philippine_today
from app.database.session import get_db
from app.models.interest_policy import InterestPolicy
from app.models.interest_record import InterestRecord
from app.models.user import User
from app.schemas.interest_record import InterestRecordCreate, InterestRecordOut

router = APIRouter(prefix="/interest-records", tags=["Layer 5 - Interest Records"])

CENT = Decimal("0.01")
# How many interest periods a year has for each compounding frequency.
PERIODS_PER_YEAR = {"DAILY": 365, "MONTHLY": 12, "QUARTERLY": 4, "YEARLY": 1}


def calculate_interest(balance: Decimal, policy: InterestPolicy) -> Decimal:
    """One period's interest: balance x annual_rate % / periods per year. Computed here, never taken from the client."""
    periods = PERIODS_PER_YEAR[policy.compounding_frequency or "MONTHLY"]
    return (balance * Decimal(policy.annual_rate) / 100 / periods).quantize(CENT, rounding=ROUND_HALF_UP)


@router.post("/", response_model=InterestRecordOut, status_code=status.HTTP_201_CREATED)
def create_interest_record(record: InterestRecordCreate, db: Session = Depends(get_db)):
    # Lock the account row — see the same note in deposits.py / withdrawals.py.
    account = lock_account(db, record.account_id)
    if account.status == "CLOSED":
        raise HTTPException(status_code=400, detail="Account is CLOSED, cannot credit interest")

    policy = db.query(InterestPolicy).filter(InterestPolicy.id == record.policy_id).first()
    if not policy:
        raise HTTPException(status_code=400, detail="policy_id does not exist")
    if policy.account_type_id != account.account_type_id:
        raise HTTPException(status_code=400, detail="This interest policy is for a different account type")
    today = philippine_today()
    if policy.effective_date > today or (policy.expiration_date and policy.expiration_date < today):
        raise HTTPException(status_code=400, detail="This interest policy is not in effect today")

    # Any amount_credited sent by the client is ignored.
    amount = calculate_interest(account.available_balance, policy)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="No interest to credit (the balance or the rate is 0)")

    # Snapshot the balance before and after crediting — computed by the
    # server, not supplied by the client.
    balance_before = account.available_balance
    new_record = InterestRecord(
        account_id=account.id,
        policy_id=policy.id,
        amount_credited=amount,
        balance_before=balance_before,
        balance_after=balance_before + amount,
    )
    db.add(new_record)
    db.flush()  # gives new_record its id, used as the ledger reference below

    credit(db, account, amount, f"INT-{new_record.id}", "INTEREST")

    commit_money(db)
    db.refresh(new_record)
    return new_record


@router.get("/", response_model=list[InterestRecordOut])
def list_interest_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(InterestRecord)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see interest on their own accounts
        query = query.filter(InterestRecord.account_id.in_(ids))
    return query.all()


@router.get("/{record_id}", response_model=InterestRecordOut)
def get_interest_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(InterestRecord).filter(InterestRecord.id == record_id).first()
    ids = own_account_ids(current_user, db)
    if not record or (ids is not None and not record.account_id in ids):
        raise HTTPException(status_code=404, detail="Interest record not found")
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interest_record(record_id: int, db: Session = Depends(get_db)):
    """Reverses the interest: the amount leaves the account again (ledger REVERSAL)."""
    record = db.query(InterestRecord).filter(InterestRecord.id == record_id).with_for_update().first()
    if not record:
        raise HTTPException(status_code=404, detail="Interest record not found")

    account = lock_account(db, record.account_id)
    debit(db, account, record.amount_credited, f"INT-{record.id}", "REVERSAL")

    db.delete(record)
    commit_money(db)
