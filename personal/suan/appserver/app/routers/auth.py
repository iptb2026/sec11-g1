from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession
from app.core.security import verify_password, generate_token

router = APIRouter(prefix="/auth", tags=["Layer 2 - Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    username: str
    role: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    role = db.query(Role).filter(Role.id == user.role_id).first()

    token = generate_token()
    session = UserSession(
        user_id=user.id,
        jwt_token=token,
        expires_at=datetime.utcnow() + timedelta(hours=8),
    )
    db.add(session)
    db.commit()

    return LoginResponse(token=token, user_id=user.id, username=user.username, role=role.role_code)


@router.post("/logout")
def logout(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if session:
        session.revoked_at = datetime.utcnow()
        db.commit()
    return {"status": "logged out"}


@router.get("/me", response_model=LoginResponse)
def me(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session or session.expires_at < datetime.utcnow() or session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.query(User).filter(User.id == session.user_id).first()
    role = db.query(Role).filter(Role.id == user.role_id).first()
    return LoginResponse(token=token, user_id=user.id, username=user.username, role=role.role_code)
