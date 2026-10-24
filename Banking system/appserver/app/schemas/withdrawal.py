# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field


class WithdrawalCreate(BaseModel):
    account_id: int
    reference_number: str
    amount: Decimal = Field(gt=0)
    withdrawal_channel: Literal["ATM", "ONLINE", "BRANCH", "INTERBANK"]
    remarks: Optional[str] = None
    # NOTE: transaction_date and approved_by_user_id are set by the server
    # (now, and the logged-in user), so a withdrawal can't be backdated or
    # recorded in someone else's name.


class WithdrawalOut(BaseModel):
    id: int
    account_id: int
    reference_number: str
    amount: Decimal
    withdrawal_channel: str
    approved_by_user_id: Optional[int] = None
    remarks: Optional[str] = None
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True