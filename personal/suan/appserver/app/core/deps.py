from datetime import datetime

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session or session.expires_at < datetime.utcnow() or session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.query(User).filter(User.id == session.user_id).first()
    role = db.query(Role).filter(Role.id == user.role_id).first()
    user.role_name = role.role_code  # attach for convenience
    return user


def require_role(*allowed_roles: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role_name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker
