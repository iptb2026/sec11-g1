from app.database.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password

db = SessionLocal()

demo_users = [
    ("admin1", "ADMIN", "admin123", "Ada", "Min"),
    ("staff1", "STAFF", "staff123", "Sam", "Staff"),
    ("cust1", "CUSTOMER", "cust123", "Cara", "Customer"),
]

for username, role_code, pw, first_name, last_name in demo_users:
    role = db.query(Role).filter(Role.role_code == role_code).first()
    if not role:
        print(f"Role {role_code} not found in roles table — check your role_code values")
        continue
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"{username} already exists, skipping")
        continue
    user = User(
        username=username,
        hashed_password=hash_password(pw),
        role_id=role.id,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(user)

db.commit()
print("Done.")
