from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.deps import get_current_user, require_role
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


# ADMIN + STAFF can open accounts for any customer
@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("ADMIN", "STAFF"))])
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == account.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    account_type = db.query(AccountType).filter(AccountType.id == account.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    existing = db.query(Account).filter(Account.account_number == account.account_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="account_number already exists")

    starting_balance = account_type.opening_deposit

    new_account = Account(
        **account.model_dump(),
        available_balance=starting_balance,
        ledger_balance=starting_balance,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


# ADMIN + STAFF see every account; CUSTOMER only sees their own
@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role_name in ("ADMIN", "STAFF"):
        return db.query(Account).all()
    return db.query(Account).filter(Account.customer_id == user.id).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if user.role_name == "CUSTOMER" and account.customer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your account")
    return account


# ADMIN + STAFF only — customers can't freeze/close their own accounts
@router.put("/{account_id}", response_model=AccountOut,
            dependencies=[Depends(require_role("ADMIN", "STAFF"))])
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

    if data.status == "CLOSED" and account.status != "CLOSED":
        account.closed_at = datetime.utcnow()

    for field, value in data.model_dump().items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return account


# Only ADMIN can delete an account
@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    commit_or_409(db, "Cannot delete this account — related transactions or records still reference it")
