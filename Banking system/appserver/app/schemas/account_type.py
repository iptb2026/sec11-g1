# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AccountTypeCreate(BaseModel):
    type_code: str
    type_name: str
    minimum_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    opening_deposit: Decimal = Field(default=Decimal("0.00"), ge=0)
    annual_interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    daily_withdrawal_limit: Decimal = Field(default=Decimal("0.00"), ge=0)


class AccountTypeOut(BaseModel):
    id: int
    type_code: str
    type_name: str
    minimum_balance: Decimal
    opening_deposit: Decimal
    annual_interest_rate: Decimal
    daily_withdrawal_limit: Decimal
    created_at: datetime

    class Config:
        from_attributes = True