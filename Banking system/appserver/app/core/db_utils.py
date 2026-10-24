from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

# MySQL error 3819: "Check constraint ... is violated". PyMySQL raises it as
# OperationalError, not IntegrityError.
MYSQL_CHECK_VIOLATION = 3819


def commit_or_409(db: Session, message: str = "This action conflicts with existing related data"):
    """
    Commit the current transaction. If the database rejects it because of a
    foreign key or unique constraint violation, roll back and turn it into a
    clean 409 response instead of letting a raw 500 (IntegrityError) escape.

    Typical case: trying to DELETE a row that other rows still reference
    (e.g. deleting a `role` that a `user` still points to).
    """
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def commit_money(db: Session):
    """
    Commit for every endpoint that changes a balance.

    If the database has a CHECK constraint on balances (the Database Admin
    guide's "balance floor", item C) and this change breaks it, MySQL
    rejects the commit. Roll back and return 400 instead of a 500, so the
    constraint can be added without breaking the API.
    """
    try:
        db.commit()
    except OperationalError as err:
        db.rollback()
        code = err.orig.args[0] if err.orig is not None and err.orig.args else None
        if code == MYSQL_CHECK_VIOLATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This would break a balance rule in the database (for example the minimum balance)",
            )
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This conflicts with existing data")
