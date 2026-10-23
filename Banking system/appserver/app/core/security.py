import uuid
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User

# Tool for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells FastAPI where users log in to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- PASSWORD FUNCTIONS ---

def hash_password(password: str) -> str:
    """Turn a plain password into a hash before saving to the database."""
    return pwd_context.hash(password)


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain password with the stored hash. Returns True or False."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT TOKEN FUNCTIONS ---

def create_token(username: str, expires_at: datetime) -> str:
    """
    Create a JWT token for a logged-in user, valid until `expires_at` (UTC).
    `jti` makes every login's token unique, so each one maps to exactly one
    row in `sessions` and logging out revokes only that login.
    """
    data = {"sub": username, "exp": expires_at, "jti": uuid.uuid4().hex}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Used on every protected route (see main.py).
    FastAPI grabs the token from the "Authorization: Bearer ..." header and
    passes it here. The request only goes through if:
      - the token is signed by us and not expired,
      - its row in `sessions` exists and was not revoked by /auth/logout,
      - the user still exists and is ACTIVE.
    Otherwise it stops with 401, which makes the frontend send the user to /login.
    Returns the logged-in User.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise _unauthorized("Invalid or expired token")

    username = payload.get("sub")
    if username is None:
        raise _unauthorized("Invalid token")

    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session or session.revoked_at is not None or session.expires_at < datetime.utcnow():
        raise _unauthorized("Session has ended, please log in again")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or user.username != username or user.account_status != "ACTIVE":
        raise _unauthorized("Account is not active")

    return user