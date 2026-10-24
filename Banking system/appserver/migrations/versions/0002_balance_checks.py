"""balance floor: accounts can't go below 0

Adds CHECK constraints so MySQL itself refuses a negative balance, even
from a bug or a manual UPDATE. The API already turns the resulting
MySQL error 3819 into a 400 and rolls back (commit_money in
app/core/db_utils.py).

Fails with error 3819 if an account is already below 0. Find it with:
    SELECT id, account_number, available_balance, ledger_balance
    FROM accounts WHERE available_balance < 0 OR ledger_balance < 0;
fix the data, then run `alembic upgrade head` again.

Revision ID: 0002_balance_checks
Revises: 0001_baseline
Create Date: 2026-10-24

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0002_balance_checks'
down_revision: Union[str, Sequence[str], None] = '0001_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint('chk_accounts_available_balance', 'accounts', 'available_balance >= 0')
    op.create_check_constraint('chk_accounts_ledger_balance', 'accounts', 'ledger_balance >= 0')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('chk_accounts_ledger_balance', 'accounts', type_='check')
    op.drop_constraint('chk_accounts_available_balance', 'accounts', type_='check')
