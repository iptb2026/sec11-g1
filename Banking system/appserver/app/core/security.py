import uuid
from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.audit import remember_request_user
from app.core.config import settings
from app.core.timeutil import utc_now
from app.database.session import get_db
from app.models.account import Account
from app.models.role import Role
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


def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Used on every protected route (see main.py).
    FastAPI grabs the token from the "Authorization: Bearer ..." header and
    passes it here. The request only goes through if:
      - the token is signed by us and not expired,
      - its row in `sessions` exists and was not revoked by /auth/logout,
      - the user still exists and is ACTIVE.
    Otherwise it stops with 401, which makes the frontend send the user to /login.
    Returns the logged-in User, and remembers them on the request's DB session
    so the automatic audit log (core/audit.py) knows who made each change.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise _unauthorized("Invalid or expired token")

    username = payload.get("sub")
    if username is None:
        raise _unauthorized("Invalid token")

    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session or session.revoked_at is not None or session.expires_at < utc_now():
        raise _unauthorized("Session has ended, please log in again")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or user.username != username or user.account_status != "ACTIVE":
        raise _unauthorized("Account is not active")

    remember_request_user(db, user.id, request)
    return user


# --- ROLE CHECKS ---

ADMIN_ONLY = ("ADMIN",)
ADMIN_STAFF = ("ADMIN", "STAFF")
ALL_ROLES = ("ADMIN", "STAFF", "CUSTOMER", "AUDITOR")
# AUDITOR: read-only access to everything an admin can read (except login
# sessions, which hold tokens), and no write access anywhere.
ADMIN_AUDITOR = ("ADMIN", "AUDITOR")
STAFF_READERS = ("ADMIN", "STAFF", "AUDITOR")


def role_code_of(user: User, db: Session) -> str | None:
    role = db.query(Role).filter(Role.id == user.role_id).first()
    return role.role_code if role else None


def require_role(user: User, db: Session, allowed: tuple) -> None:
    """Stops the request with 403 unless the user's role is in `allowed`."""
    if role_code_of(user, db) not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your role is not allowed to do this")


def roles_required(allowed: tuple):
    """Per-route guard: `dependencies=[roles_required(ADMIN_ONLY)]`. Runs before the body is validated."""
    def guard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        require_role(user, db, allowed)

    return Depends(guard)


def allow_roles(read: tuple, write: tuple):
    """
    Router-level guard used in main.py, in place of plain login_required.
    GET requests need a role in `read`; POST/PUT/DELETE need a role in `write`.
    Also requires login, since it depends on get_current_user.
    """
    def guard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        allowed = read if request.method in ("GET", "HEAD") else write
        require_role(user, db, allowed)

    return Depends(guard)


def own_account_ids(user: User, db: Session) -> list[int] | None:
    """
    For list/get endpoints that customers can read: None means "no filter"
    (ADMIN/STAFF/AUDITOR see everything); otherwise the ids of the customer's own accounts.
    """
    if role_code_of(user, db) in STAFF_READERS:
        return None
    return [a.id for a in db.query(Account.id).filter(Account.customer_id == user.id).all()]