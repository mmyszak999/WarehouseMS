"""empty message

Revision ID: a7a1bad6d864
Revises: 9b668ff1e644
Create Date: 2024-07-08 07:56:59.351259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7a1bad6d864'
down_revision = '9b668ff1e644'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('rack_level_slot', 'rack_level_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('rack_level_slot', 'rack_level_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
