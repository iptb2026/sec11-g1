# ==== LAYER 1: Foundation & Reference Data ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.security import ALL_ROLES
from app.database.session import get_db
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleOut

router = APIRouter(prefix="/roles", tags=["Layer 1 - Roles"])

# The API decides who may do what by these role codes (core/security.py).
# Renaming or deleting one would lock everyone with that role out, so their
# codes are fixed; their names and descriptions can still be edited.
BUILT_IN_ROLES = ALL_ROLES


@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.role_code == role.role_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="role_code already exists")

    new_role = Role(**role.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.get("/", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: int, role_data: RoleCreate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.role_code in BUILT_IN_ROLES and role_data.role_code != role.role_code:
        raise HTTPException(status_code=400, detail=f"{role.role_code} is a built-in role; its code cannot change")
    duplicate = db.query(Role).filter(Role.role_code == role_data.role_code, Role.id != role_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="role_code already exists")

    for field, value in role_data.model_dump().items():
        setattr(role, field, value)

    commit_or_409(db, "role_code already exists")
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.role_code in BUILT_IN_ROLES:
        raise HTTPException(status_code=400, detail=f"{role.role_code} is a built-in role and cannot be deleted")

    db.delete(role)
    commit_or_409(db, "Cannot delete this role — one or more users still reference it")