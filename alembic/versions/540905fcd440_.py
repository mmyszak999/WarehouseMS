"""empty message

Revision ID: 540905fcd440
Revises: a8e10589ea18
Create Date: 2024-07-11 10:19:36.533205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '540905fcd440'
down_revision = 'a8e10589ea18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('issue', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('product', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('rack', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('rack_level', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('rack_level_slot', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('reception', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('section', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('stock', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('waiting_room', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('warehouse', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('warehouse', 'created_at')
    op.drop_column('waiting_room', 'created_at')
    op.drop_column('user', 'created_at')
    op.drop_column('stock', 'created_at')
    op.drop_column('section', 'created_at')
    op.drop_column('reception', 'created_at')
    op.drop_column('rack_level_slot', 'created_at')
    op.drop_column('rack_level', 'created_at')
    op.drop_column('rack', 'created_at')
    op.drop_column('product', 'created_at')
    op.drop_column('issue', 'created_at')
    op.drop_column('category', 'created_at')
    # ### end Alembic commands ###