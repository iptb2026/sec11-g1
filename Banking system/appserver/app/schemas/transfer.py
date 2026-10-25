# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field, model_validator


class TransferCreate(BaseModel):
    source_account_id: int
    # Either the destination's id (staff screens) or its account number
    # (customers' Send Money: they can't see other accounts' ids).
    destination_account_id: Optional[int] = None
    destination_account_number: Optional[str] = None
    # Leave blank to let the server generate one (see app/core/references.py).
    transfer_reference: Optional[str] = None
    amount: Decimal = Field(gt=0)
    transfer_type: Literal["INTERNAL", "SCHEDULED"] = "INTERNAL"
    remarks: Optional[str] = None

    @model_validator(mode="after")
    def needs_a_destination(self):
        if self.destination_account_id is None and not (self.destination_account_number or "").strip():
            raise ValueError("destination_account_id or destination_account_number is required")
        return self


class TransferOut(BaseModel):
    id: int
    source_account_id: int
    destination_account_id: int
    transfer_reference: str
    amount: Decimal
    transfer_type: str
    remarks: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True