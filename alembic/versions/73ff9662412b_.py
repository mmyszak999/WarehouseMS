"""empty message

Revision ID: 73ff9662412b
Revises: a7a1bad6d864
Create Date: 2024-07-08 08:06:22.134499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73ff9662412b'
down_revision = 'a7a1bad6d864'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('rack_level_slot', 'rack_level_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint('rack_level_slot_rack_level_id_fkey', 'rack_level_slot', type_='foreignkey')
    op.create_foreign_key(None, 'rack_level_slot', 'rack_level', ['rack_level_id'], ['id'], onupdate='SET NULL', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rack_level_slot', type_='foreignkey')
    op.create_foreign_key('rack_level_slot_rack_level_id_fkey', 'rack_level_slot', 'rack_level', ['rack_level_id'], ['id'], onupdate='SET NULL', ondelete='SET NULL')
    op.alter_column('rack_level_slot', 'rack_level_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
