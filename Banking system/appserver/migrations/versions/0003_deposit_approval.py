"""deposit approval: large staff deposits wait for an admin

Adds deposits.status (PENDING / COMPLETED / REJECTED) and who reviewed it
and when. Every existing deposit already moved money, so they all become
COMPLETED. See needs_approval() in app/routers/deposits.py.

Revision ID: 0003_deposit_approval
Revises: 0002_balance_checks
Create Date: 2026-10-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_deposit_approval'
down_revision: Union[str, Sequence[str], None] = '0002_balance_checks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('deposits', sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'REJECTED'), nullable=False, server_default='COMPLETED'))
    op.add_column('deposits', sa.Column('reviewed_by_user_id', sa.BigInteger(), nullable=True))
    op.add_column('deposits', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_deposits_reviewed_by_user', 'deposits', 'users', ['reviewed_by_user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_deposits_reviewed_by_user', 'deposits', type_='foreignkey')
    op.drop_column('deposits', 'reviewed_at')
    op.drop_column('deposits', 'reviewed_by_user_id')
    op.drop_column('deposits', 'status')
