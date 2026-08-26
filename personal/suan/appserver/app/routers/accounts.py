from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountOut
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/accounts", tags=["Layer 3 - Accounts"])


# ADMIN + STAFF can create accounts for any customer
@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("ADMIN", "STAFF"))])
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    new_account = Account(**data.model_dump())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


# ADMIN + STAFF see every account; CUSTOMER only sees their own
@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role_name in ("ADMIN", "STAFF"):
        return db.query(Account).all()
    return db.query(Account).filter(Account.user_id == user.id).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if user.role_name == "CUSTOMER" and account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your account")
    return account


# Only ADMIN can delete an account
@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(require_role("ADMIN"))])
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
