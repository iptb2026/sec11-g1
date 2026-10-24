# ==== LAYER 5: Financial Records & Ledger ====
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class FeeRecordCreate(BaseModel):
    account_id: int
    fee_type_id: int
    transaction_reference: Optional[str] = None
    # Ignored: the server calculates the fee from the fee type
    # (fixed_amount + percentage_rate % of the transaction_reference's amount).
    # Still accepted so older clients that send it keep working.
    amount_charged: Optional[Decimal] = Field(default=None, exclude=True)
    remarks: Optional[str] = None


class FeeRecordOut(BaseModel):
    id: int
    account_id: int
    fee_type_id: int
    transaction_reference: Optional[str] = None
    amount_charged: Decimal
    charged_at: datetime
    remarks: Optional[str] = None

    class Config:
        from_attributes = True