"""Drop pay cycles

Revision ID: 352f1a704f19
Revises: 0302297c45e2
Create Date: 2018-03-29 09:27:11.032977

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '352f1a704f19'
down_revision = '0302297c45e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('paycycle_hours')
    op.drop_table('pay_cycle')
    op.add_column('hours', sa.Column('pay_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('middle_name', sa.String(length=35), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'middle_name')
    op.drop_column('hours', 'pay_date')
    op.create_table('pay_cycle',
    sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('company_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('employee_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('end', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_seen', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('time_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='pay_cycle_company_id_fkey'),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], name='pay_cycle_employee_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='pay_cycle_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('paycycle_hours',
    sa.Column('fk_hours', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('fk_pay_cycle', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['fk_hours'], ['hours.id'], name='paycycle_hours_fk_hours_fkey'),
    sa.ForeignKeyConstraint(['fk_pay_cycle'], ['pay_cycle.id'], name='paycycle_hours_fk_pay_cycle_fkey')
    )
    # ### end Alembic commands ###
