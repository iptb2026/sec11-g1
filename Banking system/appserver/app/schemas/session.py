# ==== LAYER 2: Identity & Access ====
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Sessions are only created by POST /auth/login, so there is no SessionCreate.


class SessionOut(BaseModel):
    # jwt_token / refresh_token are deliberately left out: anyone holding a
    # live token can act as that user, so the API never hands them out.
    id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True
