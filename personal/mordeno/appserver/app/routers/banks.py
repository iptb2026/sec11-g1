from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.bank import Bank
from app.schemas.bank import BankCreate, BankOut

router = APIRouter(
    prefix="/banks",
    tags=["Layer 1 - Banks"],
)


@router.get("/", response_model=list[BankOut])
def get_banks(db: Session = Depends(get_db)):
    return db.query(Bank).all()


@router.post("/", response_model=BankOut)
def create_bank(
    bank: BankCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Bank)
        .filter(Bank.bank_code == bank.bank_code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bank already exists",
        )

    new_bank = Bank(**bank.model_dump())

    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)

    return new_bank
