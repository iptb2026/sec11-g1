# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class AccountTypeCreate(BaseModel):
    type_code: str = Field(min_length=1)
    type_name: str = Field(min_length=1)
    minimum_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    opening_deposit: Decimal = Field(default=Decimal("0.00"), ge=0)
    annual_interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    # 0 means "no daily limit" for accounts of this type.
    daily_withdrawal_limit: Decimal = Field(default=Decimal("0.00"), ge=0)

    @model_validator(mode="after")
    def opening_covers_minimum(self):
        # A new account starts with opening_deposit as its balance, so it must
        # already satisfy the type's own minimum_balance rule on day one.
        if self.opening_deposit < self.minimum_balance:
            raise ValueError("opening_deposit must be at least minimum_balance")
        return self


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
