"""empty message

Revision ID: 075f8ec83065
Revises: 3c2fda2c2f50
Create Date: 2024-06-12 12:20:52.677649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '075f8ec83065'
down_revision = '3c2fda2c2f50'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('category_id_key', 'category', type_='unique')
    op.create_index(op.f('ix_category_id'), 'category', ['id'], unique=True)
    op.drop_constraint('issue_id_key', 'issue', type_='unique')
    op.create_index(op.f('ix_issue_id'), 'issue', ['id'], unique=True)
    op.drop_constraint('product_id_key', 'product', type_='unique')
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=True)
    op.drop_constraint('user_id_key', 'user', type_='unique')
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=True)
    op.drop_constraint('waiting_room_id_key', 'waiting_room', type_='unique')
    op.create_index(op.f('ix_waiting_room_id'), 'waiting_room', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_waiting_room_id'), table_name='waiting_room')
    op.create_unique_constraint('waiting_room_id_key', 'waiting_room', ['id'])
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.create_unique_constraint('user_id_key', 'user', ['id'])
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.create_unique_constraint('product_id_key', 'product', ['id'])
    op.drop_index(op.f('ix_issue_id'), table_name='issue')
    op.create_unique_constraint('issue_id_key', 'issue', ['id'])
    op.drop_index(op.f('ix_category_id'), table_name='category')
    op.create_unique_constraint('category_id_key', 'category', ['id'])
    # ### end Alembic commands ###
