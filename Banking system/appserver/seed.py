"""
Seed the database with the 4 standard roles, one demo user per role, and
the reference data Frontend needs to demo every page: account types,
banks, fee types, interest policies, and one opened account for the
demo customer.

Run once from Banking system/appserver, after MySQL is running and the
database in app/core/config.py exists:

    .\\virt\\Scripts\\python seed.py

Safe to run again: existing rows (matched by their unique code) are left alone.
"""
from datetime import date

from app.core.security import hash_password
from app.database.session import Base, SessionLocal, engine
import app.main  # noqa: F401  (imports every model so create_all sees all tables)
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.bank import Bank
from app.models.fee_type import FeeType
from app.models.interest_policy import InterestPolicy
from app.models.role import Role
from app.models.user import User
from app.models.withdrawal_limit import WithdrawalLimit

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
    ("jdelacruz", "Juan", "Dela Cruz", "jdelacruz@primebank.ph", "CUSTOMER"),
]

# (type_code, type_name, minimum_balance, opening_deposit, annual_interest_rate, daily_withdrawal_limit)
ACCOUNT_TYPES = [
    ("SAVINGS", "Regular Savings", 500, 1000, 0.25, 50000),
    ("CHECKING", "Checking Account", 2000, 5000, 0.00, 100000),
]

# (bank_code, swift_code, bank_name, short_name) — targets for interbank transfers
BANKS = [
    ("BDO", "BNORPHMM", "BDO Unibank, Inc.", "BDO"),
    ("BPI", "BOPIPHMM", "Bank of the Philippine Islands", "BPI"),
]

# (fee_code, fee_name, fee_description, fixed_amount, percentage_rate)
FEE_TYPES = [
    ("MAINT", "Below Maintaining Balance", "Monthly fee when the balance falls below the minimum", 300, 0),
    ("INTERBANK", "Interbank Transfer Fee", "Charged per interbank transfer", 25, 0),
]

# (account_type_code, policy_name, annual_rate, compounding_frequency)
INTEREST_POLICIES = [
    ("SAVINGS", "Savings Standard Rate", 0.25, "MONTHLY"),
]

# (account_number, owner_username, account_type_code) — opened with the type's opening_deposit
ACCOUNTS = [
    ("1000000001", "jdelacruz", "SAVINGS"),
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

        type_ids = {}
        for code, name, min_bal, opening, rate, daily_limit in ACCOUNT_TYPES:
            account_type = db.query(AccountType).filter(AccountType.type_code == code).first()
            if not account_type:
                account_type = AccountType(
                    type_code=code,
                    type_name=name,
                    minimum_balance=min_bal,
                    opening_deposit=opening,
                    annual_interest_rate=rate,
                    daily_withdrawal_limit=daily_limit,
                )
                db.add(account_type)
                db.flush()
                print(f"Added account type {code}")
            type_ids[code] = account_type

        for code, swift, name, short in BANKS:
            if db.query(Bank).filter(Bank.bank_code == code).first():
                continue
            db.add(Bank(bank_code=code, swift_code=swift, bank_name=name, short_name=short, status="ACTIVE"))
            print(f"Added bank {code}")

        for code, name, description, fixed, pct in FEE_TYPES:
            if db.query(FeeType).filter(FeeType.fee_code == code).first():
                continue
            db.add(FeeType(fee_code=code, fee_name=name, fee_description=description,
                           fixed_amount=fixed, percentage_rate=pct))
            print(f"Added fee type {code}")

        for type_code, name, rate, frequency in INTEREST_POLICIES:
            if db.query(InterestPolicy).filter(InterestPolicy.policy_name == name).first():
                continue
            db.add(InterestPolicy(account_type_id=type_ids[type_code].id, policy_name=name,
                                  annual_rate=rate, compounding_frequency=frequency,
                                  effective_date=date(2026, 1, 1)))
            print(f"Added interest policy {name}")

        db.flush()

        for number, username, type_code in ACCOUNTS:
            if db.query(Account).filter(Account.account_number == number).first():
                continue
            owner = db.query(User).filter(User.username == username).first()
            account_type = type_ids[type_code]
            # Same rule as POST /accounts: the starting balance is the type's
            # opening_deposit, so account_balance_audit reconciles to zero.
            account = Account(
                account_number=number,
                customer_id=owner.id,
                account_type_id=account_type.id,
                available_balance=account_type.opening_deposit,
                ledger_balance=account_type.opening_deposit,
            )
            db.add(account)
            db.flush()
            db.add(WithdrawalLimit(account_id=account.id,
                                   daily_limit_amount=account_type.daily_withdrawal_limit,
                                   last_reset_date=date.today()))
            print(f"Added account {number} for {username} ({type_code})")

        db.commit()
        print("Done. Log in with any seeded username and DEMO_PASSWORD from seed.py.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
