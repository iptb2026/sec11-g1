# ==== LAYER 3: Account Configuration ====
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.money import credit
from app.core.security import get_current_user, own_account_ids
from app.core.timeutil import utc_now
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.ledger_entry import LedgerEntry
from app.models.user import User
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


ACCOUNT_NUMBER_BASE = 1000000000


def account_number_for(account_id: int) -> str:
    """
    The account number for a new account: 1000000000 + its database id
    (id 15 -> "1000000015"). MySQL hands out every id exactly once, so two
    accounts opened at the same moment can never get the same number.
    """
    return str(ACCOUNT_NUMBER_BASE + account_id)


def opening_reference(account: Account) -> str:
    return f"OPEN-{account.account_number}"


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == account.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(AccountType.id == account.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    typed_number = (account.account_number or "").strip()
    if typed_number:
        existing = db.query(Account).filter(Account.account_number == typed_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="account_number already exists")

    # The starting balance comes from the account type's opening_deposit —
    # never from the client. This is the same "don't trust the client with
    # money fields" lesson from AccountCreate in the old single-table version.
    starting_balance = account_type.opening_deposit

    data = account.model_dump()
    # Blank account number: the number comes from the database id, which only
    # exists after the insert. Insert with a unique placeholder first, then set
    # the real number in the same transaction.
    data["account_number"] = typed_number or f"PENDING-{uuid.uuid4().hex[:20]}"
    new_account = Account(**data, available_balance=0, ledger_balance=0)
    db.add(new_account)
    db.flush()  # gives new_account its id for the account number and ledger row
    if not typed_number:
        new_account.account_number = account_number_for(new_account.id)
        try:
            db.flush()
        except IntegrityError:
            # Someone typed this exact number by hand earlier.
            db.rollback()
            raise HTTPException(status_code=409, detail="The generated account number is already taken; enter one manually")
    if starting_balance:
        # The opening deposit is the account's first ledger entry.
        credit(db, new_account, starting_balance, opening_reference(new_account), "DEPOSIT")
    # The account type's daily withdrawal limit applies from day one (as in seed.py).
    # Staff can still change it on the Withdrawal Limits page.
    if account_type.daily_withdrawal_limit:
        db.add(WithdrawalLimit(
            account_id=new_account.id,
            daily_limit_amount=account_type.daily_withdrawal_limit,
            last_reset_date=utc_now().date(),
        ))
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Account)
    ids = own_account_ids(current_user, db)
    if ids is not None:  # customers only see their own accounts' rows
        query = query.filter(Account.id.in_(ids))
    return query.all()


@router.get("/next-number")
def next_account_number(db: Session = Depends(get_db)):
    """
    The number the next new account will get (1000000000 + the next id), so the
    New Account form can show it. Opening the account still assigns the real
    number: if two people open accounts at the same moment, one of them gets
    the following number, and the save message shows the final one.
    """
    # MySQL caches AUTO_INCREMENT in information_schema (up to a day by
    # default); expiry 0 makes this read the current value.
    db.execute(text("SET SESSION information_schema_stats_expiry = 0"))
    next_id = db.execute(text(
        "SELECT AUTO_INCREMENT FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'accounts'"
    )).scalar()
    if not next_id:
        next_id = (db.query(func.max(Account.id)).scalar() or 0) + 1
    return {"account_number": account_number_for(next_id)}


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    ids = own_account_ids(current_user, db)
    if not account or (ids is not None and not account.id in ids):
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    customer = db.query(User).filter(User.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(AccountType.id == data.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    duplicate = db.query(Account).filter(
        Account.account_number == data.account_number, Account.id != account_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="account_number already exists")

    if data.status == "CLOSED" and account.status != "CLOSED":
        account.closed_at = utc_now()

    for field, value in data.model_dump().items():
        setattr(account, field, value)

    commit_or_409(db, "account_number already exists")
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # An account that was never used has only its opening ledger row; remove
    # it so the account can still be deleted. Any other ledger row (a real
    # transaction) keeps the delete blocked below.
    entries = db.query(LedgerEntry).filter(LedgerEntry.account_id == account.id).all()
    if len(entries) == 1 and entries[0].transaction_reference == opening_reference(account):
        db.delete(entries[0])
        db.flush()  # the ledger row must be gone before the account row

    # Its withdrawal limit row only describes the account, so it goes too.
    # If anything else still references the account, the commit below fails
    # and rolls this back as well.
    for limit in db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).all():
        db.delete(limit)  # one by one, so the audit log records it
    db.flush()

    db.delete(account)
    commit_or_409(db, "Cannot delete this account — related transactions or records still reference it")