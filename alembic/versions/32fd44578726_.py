"""empty message

Revision ID: 32fd44578726
Revises: 
Create Date: 2024-10-09 06:19:01.250687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32fd44578726'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=75), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_category_id'), 'category', ['id'], unique=True)
    op.create_table('product',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=75), nullable=False),
    sa.Column('wholesale_price', sa.DECIMAL(), nullable=False),
    sa.Column('amount_in_goods', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.Column('weight', sa.DECIMAL(), nullable=False),
    sa.Column('legacy_product', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=75), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('employment_date', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_staff', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('has_password_set', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('can_move_stocks', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('can_recept_stocks', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('can_issue_stocks', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=True)
    op.create_table('warehouse',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('warehouse_name', sa.String(length=400), nullable=False),
    sa.Column('max_sections', sa.Integer(), nullable=False),
    sa.Column('available_sections', sa.Integer(), nullable=False),
    sa.Column('occupied_sections', sa.Integer(), nullable=False),
    sa.Column('max_waiting_rooms', sa.Integer(), nullable=False),
    sa.Column('available_waiting_rooms', sa.Integer(), nullable=False),
    sa.Column('occupied_waiting_rooms', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_id'), 'warehouse', ['id'], unique=True)
    op.create_table('category_product_association_table',
    sa.Column('category_id', sa.String(), nullable=True),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='cascade')
    )
    op.create_table('issue',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('issue_date', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(length=400), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_issue_id'), 'issue', ['id'], unique=True)
    op.create_table('reception',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('reception_date', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(length=400), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('section',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('section_name', sa.String(length=400), nullable=False),
    sa.Column('max_weight', sa.DECIMAL(), nullable=False),
    sa.Column('available_weight', sa.DECIMAL(), nullable=False),
    sa.Column('occupied_weight', sa.DECIMAL(), nullable=False),
    sa.Column('reserved_weight', sa.DECIMAL(), nullable=False),
    sa.Column('weight_to_reserve', sa.DECIMAL(), nullable=False),
    sa.Column('max_racks', sa.Integer(), nullable=False),
    sa.Column('available_racks', sa.DECIMAL(), nullable=False),
    sa.Column('occupied_racks', sa.Integer(), nullable=False),
    sa.Column('warehouse_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], onupdate='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_section_id'), 'section', ['id'], unique=True)
    op.create_table('waiting_room',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=400), nullable=True),
    sa.Column('max_stocks', sa.Integer(), nullable=False),
    sa.Column('max_weight', sa.DECIMAL(), nullable=False),
    sa.Column('occupied_slots', sa.Integer(), nullable=False),
    sa.Column('available_slots', sa.Integer(), nullable=False),
    sa.Column('current_stock_weight', sa.DECIMAL(), nullable=False),
    sa.Column('available_stock_weight', sa.DECIMAL(), nullable=False),
    sa.Column('warehouse_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_waiting_room_id'), 'waiting_room', ['id'], unique=True)
    op.create_table('rack',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('rack_name', sa.String(length=400), nullable=False),
    sa.Column('max_weight', sa.DECIMAL(), nullable=False),
    sa.Column('available_weight', sa.DECIMAL(), nullable=False),
    sa.Column('occupied_weight', sa.DECIMAL(), nullable=False),
    sa.Column('max_levels', sa.Integer(), nullable=False),
    sa.Column('available_levels', sa.Integer(), nullable=False),
    sa.Column('occupied_levels', sa.Integer(), nullable=False),
    sa.Column('reserved_weight', sa.DECIMAL(), nullable=False),
    sa.Column('weight_to_reserve', sa.DECIMAL(), nullable=False),
    sa.Column('section_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['section.id'], onupdate='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rack_id'), 'rack', ['id'], unique=True)
    op.create_table('rack_level',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('rack_level_number', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=400), nullable=True),
    sa.Column('max_weight', sa.DECIMAL(), nullable=False),
    sa.Column('available_weight', sa.DECIMAL(), nullable=False),
    sa.Column('occupied_weight', sa.DECIMAL(), nullable=False),
    sa.Column('max_slots', sa.Integer(), nullable=False),
    sa.Column('available_slots', sa.Integer(), nullable=False),
    sa.Column('occupied_slots', sa.Integer(), nullable=False),
    sa.Column('active_slots', sa.Integer(), nullable=False),
    sa.Column('inactive_slots', sa.Integer(), nullable=False),
    sa.Column('rack_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rack_id'], ['rack.id'], onupdate='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rack_level_id'), 'rack_level', ['id'], unique=True)
    op.create_table('rack_level_slot',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('rack_level_slot_number', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('rack_level_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rack_level_id'], ['rack_level.id'], onupdate='SET NULL', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rack_level_slot_id'), 'rack_level_slot', ['id'], unique=True)
    op.create_table('stock',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('weight', sa.DECIMAL(), nullable=False),
    sa.Column('product_id', sa.String(), nullable=True),
    sa.Column('reception_id', sa.String(), nullable=True),
    sa.Column('issue_id', sa.String(), nullable=True),
    sa.Column('waiting_room_id', sa.String(), nullable=True),
    sa.Column('product_count', sa.Integer(), nullable=False),
    sa.Column('is_issued', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('rack_level_slot_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['rack_level_slot_id'], ['rack_level_slot.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reception_id'], ['reception.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['waiting_room_id'], ['waiting_room.id'], onupdate='cascade', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user_stock',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('stock_id', sa.String(), nullable=False),
    sa.Column('moved_at', sa.DateTime(), nullable=True),
    sa.Column('from_waiting_room_id', sa.String(), nullable=True),
    sa.Column('to_waiting_room_id', sa.String(), nullable=True),
    sa.Column('issue_id', sa.String(), nullable=True),
    sa.Column('reception_id', sa.String(), nullable=True),
    sa.Column('to_rack_level_slot_id', sa.String(), nullable=True),
    sa.Column('from_rack_level_slot_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['from_rack_level_slot_id'], ['rack_level_slot.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['from_waiting_room_id'], ['waiting_room.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reception_id'], ['reception.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['stock_id'], ['stock.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['to_rack_level_slot_id'], ['rack_level_slot.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['to_waiting_room_id'], ['waiting_room.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_stock')
    op.drop_table('stock')
    op.drop_index(op.f('ix_rack_level_slot_id'), table_name='rack_level_slot')
    op.drop_table('rack_level_slot')
    op.drop_index(op.f('ix_rack_level_id'), table_name='rack_level')
    op.drop_table('rack_level')
    op.drop_index(op.f('ix_rack_id'), table_name='rack')
    op.drop_table('rack')
    op.drop_index(op.f('ix_waiting_room_id'), table_name='waiting_room')
    op.drop_table('waiting_room')
    op.drop_index(op.f('ix_section_id'), table_name='section')
    op.drop_table('section')
    op.drop_table('reception')
    op.drop_index(op.f('ix_issue_id'), table_name='issue')
    op.drop_table('issue')
    op.drop_table('category_product_association_table')
    op.drop_index(op.f('ix_warehouse_id'), table_name='warehouse')
    op.drop_table('warehouse')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_category_id'), table_name='category')
    op.drop_table('category')
    # ### end Alembic commands ###
