# ==== LAYER 2: Identity & Access ====
from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.email import OptionalEmail

MIN_PASSWORD_LENGTH = 8


class UserCreate(BaseModel):
    username: str
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)
    email: OptionalEmail = None
    mobile_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    role_id: int
    account_status: Literal["ACTIVE", "LOCKED", "DISABLED"] = "ACTIVE"


class UserUpdate(UserCreate):
    # Blank or missing password on edit = keep the current one.
    password: Optional[str] = None
    # Needed only when users change their OWN password (see update_user).
    current_password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def new_password_long_enough(cls, value):
        if value and len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        return value


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    role_id: int
    account_status: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True