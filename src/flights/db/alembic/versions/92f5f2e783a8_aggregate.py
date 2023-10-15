"""aggregate

Revision ID: 92f5f2e783a8
Revises: 6301c4242caf
Create Date: 2023-10-15 13:55:19.469130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92f5f2e783a8'
down_revision = '6301c4242caf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('flight_aggregates',
    sa.Column('sample_entry_date_utc', sa.DateTime(), nullable=False),
    sa.Column('number_of_flights', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('sample_entry_date_utc')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('flight_aggregates')
    # ### end Alembic commands ###
