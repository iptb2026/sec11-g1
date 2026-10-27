"""
Seed the database with the 4 standard roles and one demo user per role.

Run once from Banking system/appserver, after MySQL is running and the
database in app/core/config.py exists:

    .\\virt\\Scripts\\python seed.py

Safe to run again: existing roles/users are left alone.
"""
from app.core.security import hash_password
from app.database.session import Base, SessionLocal, engine
import app.main  # noqa: F401  (imports every model so create_all sees all tables)
from app.models.role import Role
from app.models.user import User

# Demo password for every seeded user — local home lab only, change it for a real server.
DEMO_PASSWORD = "password123"

ROLES = [
    ("ADMIN", "Admin", "System Administrator"),
    ("STAFF", "Staff", "Bank staff user"),
    ("CUSTOMER", "Customer", "Bank customer"),
    ("AUDITOR", "Auditor", "Read-only compliance auditor"),
]

USERS = [
    ("admin", "System", "Administrator", "admin@minibank.com", "ADMIN"),
    ("teller1", "Maria", "Santos", "teller1@minibank.com", "STAFF"),
    ("juandelacruz", "Juan", "Dela Cruz", "juan@example.com", "CUSTOMER"),
    # Test accounts, one per role, for trying out the system.
    ("testadmin", "Test", "Admin", "testadmin@minibank.com", "ADMIN"),
    ("teststaff", "Test", "Staff", "teststaff@minibank.com", "STAFF"),
    ("testcustomer", "Test", "Customer", "testcustomer@example.com", "CUSTOMER"),
    ("testcustomer2", "Test", "Customer Two", "testcustomer2@example.com", "CUSTOMER"),
    ("testauditor", "Test", "Auditor", "testauditor@minibank.com", "AUDITOR"),
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        role_ids = {}
        for code, name, description in ROLES:
            role = db.query(Role).filter(Role.role_code == code).first()
            if not role:
                role = Role(role_code=code, role_name=name, description=description)
                db.add(role)
                db.flush()
                print(f"Added role {code}")
            role_ids[code] = role.id

        for username, first, last, email, role_code in USERS:
            if db.query(User).filter(User.username == username).first():
                continue
            db.add(User(
                username=username,
                hashed_password=hash_password(DEMO_PASSWORD),
                first_name=first,
                last_name=last,
                email=email,
                role_id=role_ids[role_code],
                account_status="ACTIVE",
            ))
            print(f"Added user {username} ({role_code})")

        db.commit()
        print("Done. Log in with any seeded username and DEMO_PASSWORD from seed.py.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
