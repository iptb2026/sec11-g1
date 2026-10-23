# ==== LAYER 2: Identity & Access ====
from pydantic import BaseModel

from app.schemas.user import UserOut


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(UserOut):
    """The logged-in user plus their role, returned by GET /auth/me."""
    role_code: str
    role_name: str
