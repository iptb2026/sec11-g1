# ==== LAYER 3: Account Configuration ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.account_rules import get_or_create_withdrawal_limit
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.role import Role
from app.models.user import User
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


def validate_customer(db: Session, customer_id: int) -> User:
    """Only an ACTIVE user with the CUSTOMER role can own a bank account."""
    customer = db.query(User).filter(User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    role = db.query(Role).filter(Role.id == customer.role_id).first()
    if not role or role.role_code != "CUSTOMER":
        raise HTTPException(status_code=400, detail="customer_id must belong to a user with the CUSTOMER role")

    if customer.account_status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Customer is {customer.account_status}, cannot own an account")
    return customer


def validate_account_type(db: Session, account_type_id: int) -> AccountType:
    account_type = db.query(AccountType).filter(AccountType.id == account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")
    return account_type


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    validate_customer(db, account.customer_id)
    account_type = validate_account_type(db, account.account_type_id)

    existing = db.query(Account).filter(Account.account_number == account.account_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="account_number already exists")

    # The starting balance comes from the account type's opening_deposit —
    # never from the client. This is the same "don't trust the client with
    # money fields" lesson from AccountCreate in the old single-table version.
    starting_balance = account_type.opening_deposit

    new_account = Account(
        **account.model_dump(),
        available_balance=starting_balance,
        ledger_balance=starting_balance,
        status="ACTIVE",
    )
    db.add(new_account)
    db.flush()

    # Every account starts with the daily withdrawal limit of its type
    # (skipped when the type's limit is 0 = no limit).
    get_or_create_withdrawal_limit(db, new_account)

    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    validate_customer(db, data.customer_id)
    account_type = validate_account_type(db, data.account_type_id)

    duplicate = db.query(Account).filter(
        Account.account_number == data.account_number, Account.id != account_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="account_number already exists")

    type_changed = data.account_type_id != account.account_type_id
    if type_changed and account.available_balance < account_type.minimum_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Balance is below the new account type's minimum balance of {account_type.minimum_balance}",
        )

    if data.status == "CLOSED" and account.status != "CLOSED":
        account.closed_at = datetime.utcnow()
    elif data.status != "CLOSED":
        account.closed_at = None

    for field, value in data.model_dump().items():
        setattr(account, field, value)

    # Switching account type also switches the daily withdrawal limit to the new type's.
    if type_changed:
        limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).first()
        if limit and account_type.daily_withdrawal_limit:
            limit.daily_limit_amount = account_type.daily_withdrawal_limit
        elif limit:
            db.delete(limit)
        else:
            get_or_create_withdrawal_limit(db, account)

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # The withdrawal limit is configuration owned by this account — remove it
    # with the account. Transactions still block the delete (409) as before.
    db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).delete()
    db.delete(account)
    commit_or_409(db, "Cannot delete this account — related transactions or records still reference it")
