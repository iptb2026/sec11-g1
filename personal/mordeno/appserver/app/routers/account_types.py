from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.account_type import AccountType
from app.schemas.account_type import AccountTypeCreate, AccountTypeOut

router = APIRouter(
    prefix="/account-types",
    tags=["Layer 1 - Account Types"],
)


@router.get("/", response_model=list[AccountTypeOut])
def get_account_types(db: Session = Depends(get_db)):
    return db.query(AccountType).all()


@router.post("/", response_model=AccountTypeOut)
def create_account_type(
    account_type: AccountTypeCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(AccountType)
        .filter(AccountType.type_code == account_type.type_code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Account type already exists",
        )

    new_account_type = AccountType(**account_type.model_dump())

    db.add(new_account_type)
    db.commit()
    db.refresh(new_account_type)

    return new_account_type
