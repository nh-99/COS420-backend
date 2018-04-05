"""Use ranges instead of start and finish times

Revision ID: dce5239a0c29
Revises: 652b758cd43c
Create Date: 2018-03-29 22:46:49.165722

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import DateTimeRangeType

# revision identifiers, used by Alembic.
revision = 'dce5239a0c29'
down_revision = '652b758cd43c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hours', sa.Column('time_range', DateTimeRangeType(), nullable=True))
    op.drop_column('hours', 'start')
    op.drop_column('hours', 'end')
    op.add_column('pay_cycle', sa.Column('time_range', DateTimeRangeType(), nullable=True))
    op.drop_column('pay_cycle', 'start')
    op.drop_column('pay_cycle', 'end')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pay_cycle', sa.Column('end', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('pay_cycle', sa.Column('start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('pay_cycle', 'time_range')
    op.add_column('hours', sa.Column('end', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('hours', sa.Column('start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('hours', 'time_range')
    # ### end Alembic commands ###
