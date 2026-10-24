"""
Set a user's password directly in the database, e.g. before a demo when
nobody remembers the admin's password.

Run from Banking system/appserver:

    .\\virt\\Scripts\\python set_password.py admin          # asks for the new password
    .\\virt\\Scripts\\python set_password.py admin s3cret   # or pass it

The password is stored as a bcrypt hash, the same way the API stores it.
The user's open sessions are ended, so they log in again with the new one.
"""
import getpass
import sys

from app.core.security import hash_password
from app.core.timeutil import utc_now
from app.database.session import SessionLocal
import app.main  # noqa: F401  (imports every model)
from app.models.session import UserSession
from app.models.user import User


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python set_password.py <username> [new password]")
    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else getpass.getpass(f"New password for {username}: ")
    if len(password) < 8:
        sys.exit("Use at least 8 characters.")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            sys.exit(f"No user named {username}.")
        user.hashed_password = hash_password(password)
        ended = (
            db.query(UserSession)
            .filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None))
            .update({UserSession.revoked_at: utc_now()}, synchronize_session=False)
        )
        db.commit()
        print(f"Password changed for {username}; {ended} open session(s) ended.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
