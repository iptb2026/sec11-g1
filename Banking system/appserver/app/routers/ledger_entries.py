# ==== LAYER 5: Financial Records & Ledger ====
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.ledger_entry import LedgerEntry
from app.schemas.ledger_entry import LedgerEntryOut

router = APIRouter(prefix="/ledger-entries", tags=["Layer 5 - Ledger Entries"])

# The ledger is written automatically: every endpoint that changes a balance
# (opening an account, deposits, withdrawals, transfers, interbank transfers,
# fees, interest, and the reversals done by their DELETEs) adds its own rows
# through app/core/money.py, at the moment it changes the balance. So this
# router is read-only: entries typed in by hand, or deleted, would make the
# ledger disagree with the balances.


@router.get("/", response_model=list[LedgerEntryOut])
def list_ledger_entries(db: Session = Depends(get_db)):
    return db.query(LedgerEntry).all()


@router.get("/{entry_id}", response_model=LedgerEntryOut)
def get_ledger_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(LedgerEntry).filter(LedgerEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return entry
