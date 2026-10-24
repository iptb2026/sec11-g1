# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class FeeTypeCreate(BaseModel):
    fee_code: str
    fee_name: str
    fee_description: Optional[str] = None
    fixed_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    percentage_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)


class FeeTypeOut(BaseModel):
    id: int
    fee_code: str
    fee_name: str
    fee_description: Optional[str] = None
    fixed_amount: Decimal
    percentage_rate: Decimal
    created_at: datetime

    class Config:
        from_attributes = True