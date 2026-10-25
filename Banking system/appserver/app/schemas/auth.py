# ==== LAYER 2: Identity & Access ====
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.email import OptionalEmail
from app.schemas.user import MIN_PASSWORD_LENGTH, UserOut


class RegisterIn(BaseModel):
    """Public sign-up (POST /auth/register). There is no role field: the
    account is always a CUSTOMER, so nobody can sign themselves up as staff."""
    username: str = Field(min_length=3, max_length=100, pattern=r"^[A-Za-z0-9._-]+$")
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: OptionalEmail = None
    mobile_number: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(UserOut):
    """The logged-in user plus their role, returned by GET /auth/me."""
    role_code: str
    role_name: str
