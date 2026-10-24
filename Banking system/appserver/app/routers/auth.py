# ==== LAYER 2: Identity & Access ====
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.audit import remember_request_user
from app.core.config import settings
from app.core.login_guard import check_not_blocked, record_failure, record_success
from app.core.security import check_password, create_token, get_current_user, oauth2_scheme
from app.core.timeutil import utc_now
from app.database.session import get_db
from app.models.role import Role
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import MeOut, Token
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["Layer 2 - Auth"])


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    check_not_blocked(form_data.username)

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not check_password(form_data.password, user.hashed_password):
        record_failure(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    record_success(form_data.username)

    remember_request_user(db, user.id, request)  # the LOGIN audit row belongs to this user
    expires_at = utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_token(user.username, expires_at)

    # Every successful login is recorded as a row in `sessions` (Layer 2 table).
    new_session = UserSession(
        user_id=user.id,
        jwt_token=token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )
    db.add(new_session)

    user.last_login_at = utc_now()

    db.commit()
    return Token(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    remember_request_user(db, session.user_id, request)  # the LOGOUT audit row belongs to this user
    session.revoked_at = utc_now()
    db.commit()


@router.get("/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Who is logged in, and with which role. Any logged-in user may call this."""
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    return MeOut(
        **UserOut.model_validate(current_user).model_dump(),
        role_code=role.role_code if role else "",
        role_name=role.role_name if role else "",
    )
