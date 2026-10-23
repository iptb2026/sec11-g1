# ==== LAYER 2: Identity & Access ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.security import (
    ADMIN_ONLY, ADMIN_STAFF, get_current_user, hash_password, require_role, role_code_of, roles_required,
)
from app.database.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Layer 2 - Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             dependencies=[roles_required(ADMIN_ONLY)])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # role_id is a foreign key — the referenced role must already exist.
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="role_id does not exist")

    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="username or email already in use")

    data = user.model_dump(exclude={"password"})
    new_user = User(**data, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserOut], dependencies=[roles_required(ADMIN_STAFF)])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        require_role(current_user, db, ADMIN_STAFF)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    is_admin = role_code_of(current_user, db) == "ADMIN"
    if user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="You can only edit your own profile")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="role_id does not exist")

    # Only an admin may change who someone is or what they can do. Everyone else
    # editing their own profile keeps their username, role and status.
    protected = set() if is_admin else {"username", "role_id", "account_status"}
    data = user_data.model_dump(exclude={"password"} | protected)
    for field, value in data.items():
        setattr(user, field, value)
    user.hashed_password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[roles_required(ADMIN_ONLY)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    commit_or_409(db, "Cannot delete this user — related sessions, accounts, or audit logs still reference it")