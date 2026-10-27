# ==== LAYER 3: Account Configuration ====
from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, TIMESTAMP, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.sql import func

from app.database.session import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        # Index behind the customer_id foreign key; already exists in the team database.
        Index("idx_accounts_customer_id", "customer_id"),
        # Balance floor: MySQL itself refuses a negative balance, even from a bug
        # or a manual UPDATE. The API turns the error into a 400 (commit_money).
        # Added to existing databases by migration 0002_balance_checks.
        CheckConstraint("available_balance >= 0", name="chk_accounts_available_balance"),
        CheckConstraint("ledger_balance >= 0", name="chk_accounts_ledger_balance"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_number = Column(String(30), unique=True, nullable=False)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    account_type_id = Column(BigInteger, ForeignKey("account_types.id"), nullable=False)
    available_balance = Column(DECIMAL(18, 2), default=0.00)
    ledger_balance = Column(DECIMAL(18, 2), default=0.00)
    currency_code = Column(String(10), default="PHP")
    status = Column(Enum("ACTIVE", "FROZEN", "CLOSED"), default="ACTIVE")
    opened_at = Column(TIMESTAMP, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    branch_code = Column(String(50), nullable=True)