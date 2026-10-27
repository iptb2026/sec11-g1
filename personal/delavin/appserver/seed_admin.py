"""
Script to create or update the admin user with a properly bcrypt-hashed password '1234'.
Run with: python seed_admin.py
"""
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

def seed_admin():
    db = SessionLocal()
    try:
        # 1. Ensure ADMIN role exists
        admin_role = db.query(Role).filter(Role.role_code == "ADMIN").first()
        if not admin_role:
            print("Creating ADMIN role...")
            admin_role = Role(
                role_code="ADMIN",
                role_name="Admin",
                description="System Administrator"
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"ADMIN role created with ID {admin_role.id}")
        else:
            print(f"Found existing ADMIN role (ID: {admin_role.id})")

        # 2. Ensure admin user exists with hashed password
        admin_user = db.query(User).filter(User.username == "admin").first()
        hashed = hash_password("1234")

        if admin_user:
            print("Updating existing 'admin' user password with proper bcrypt hash...")
            admin_user.hashed_password = hashed
            admin_user.account_status = "ACTIVE"
            admin_user.role_id = admin_role.id
            db.commit()
            print("Admin user updated successfully!")
        else:
            print("Creating new 'admin' user...")
            admin_user = User(
                username="admin",
                hashed_password=hashed,
                first_name="Admin",
                last_name="User",
                role_id=admin_role.id,
                account_status="ACTIVE"
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully!")

        print("\nSUCCESS: You can now log in with:")
        print("  Username: admin")
        print("  Password: 1234")

    except Exception as e:
        print(f"Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()

