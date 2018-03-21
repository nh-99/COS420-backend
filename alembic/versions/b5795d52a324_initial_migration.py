"""Initial migration

Revision ID: b5795d52a324
Revises:
Create Date: 2018-03-21 01:38:54.487497

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import UUIDType


# revision identifiers, used by Alembic.
revision = 'b5795d52a324'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', UUIDType(binary=False), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company',
        sa.Column('id', UUIDType(binary=False), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('employee',
        sa.Column('id', UUIDType(binary=False), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paycycle_hours',
        sa.Column('id', UUIDType(binary=False), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pay_cycle',
        sa.Column('id', UUIDType(binary=False), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hours',
        sa.Column('id', UUIDType(binary=False), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
