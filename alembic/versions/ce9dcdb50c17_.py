"""empty message

Revision ID: ce9dcdb50c17
Revises: 655a2dbdc74f
Create Date: 2024-06-13 18:12:11.159461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce9dcdb50c17'
down_revision = '655a2dbdc74f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('warehouse',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('warehouse_name', sa.String(length=400), nullable=False),
    sa.Column('max_sections', sa.Integer(), nullable=False),
    sa.Column('available_sections', sa.Integer(), nullable=False),
    sa.Column('max_waiting_rooms', sa.Integer(), nullable=False),
    sa.Column('available_waiting_rooms', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_id'), 'warehouse', ['id'], unique=True)
    op.create_table('section',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('section_name', sa.String(length=400), nullable=False),
    sa.Column('max_weight', sa.DECIMAL(), nullable=False),
    sa.Column('available_weight', sa.DECIMAL(), nullable=False),
    sa.Column('max_racks', sa.Integer(), nullable=False),
    sa.Column('available_racks', sa.DECIMAL(), nullable=False),
    sa.Column('warehouse_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], onupdate='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_section_id'), 'section', ['id'], unique=True)
    op.add_column('waiting_room', sa.Column('name', sa.String(length=400), nullable=True))
    op.add_column('waiting_room', sa.Column('warehouse_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'waiting_room', 'warehouse', ['warehouse_id'], ['id'], onupdate='cascade', ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'waiting_room', type_='foreignkey')
    op.drop_column('waiting_room', 'warehouse_id')
    op.drop_column('waiting_room', 'name')
    op.drop_index(op.f('ix_section_id'), table_name='section')
    op.drop_table('section')
    op.drop_index(op.f('ix_warehouse_id'), table_name='warehouse')
    op.drop_table('warehouse')
    # ### end Alembic commands ###
