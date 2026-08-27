from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.fee_type import FeeType
from app.schemas.fee_type import FeeTypeCreate, FeeTypeOut

router = APIRouter(
    prefix="/fee-types",
    tags=["Layer 1 - Fee Types"],
)


@router.get("/", response_model=list[FeeTypeOut])
def get_fee_types(db: Session = Depends(get_db)):
    return db.query(FeeType).all()


@router.post("/", response_model=FeeTypeOut)
def create_fee_type(
    fee_type: FeeTypeCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(FeeType)
        .filter(FeeType.fee_code == fee_type.fee_code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Fee type already exists",
        )

    new_fee_type = FeeType(**fee_type.model_dump())

    db.add(new_fee_type)
    db.commit()
    db.refresh(new_fee_type)

    return new_fee_type
