"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pharmacies table
    op.create_table(
        'pharmacies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pharmacy_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_pharmacies_pharmacy_id', 'pharmacies', ['pharmacy_id'], unique=True)
    op.create_index('ix_pharmacies_phone_number', 'pharmacies', ['phone_number'], unique=True)

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cip13', sa.String(length=13), nullable=False),
        sa.Column('ean', sa.String(length=13), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('supplier_code', sa.String(length=50), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('stock_available', sa.Integer(), nullable=True),
        sa.Column('stock_reserved', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_cip13', 'products', ['cip13'], unique=True)
    op.create_index('ix_products_name', 'products', ['name'], unique=False)

    # Create calls table
    op.create_table(
        'calls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('call_id', sa.String(length=100), nullable=False),
        sa.Column('pharmacy_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('confidence_global', sa.Float(), nullable=True),
        sa.Column('audio_recording_url', sa.String(length=500), nullable=True),
        sa.Column('agent_version', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pharmacy_id'], ['pharmacies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calls_call_id', 'calls', ['call_id'], unique=True)

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.String(length=100), nullable=False),
        sa.Column('call_id', sa.Integer(), nullable=False),
        sa.Column('pharmacy_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('delivery_date', sa.Date(), nullable=True),
        sa.Column('delivery_notes', sa.Text(), nullable=True),
        sa.Column('required_human_review', sa.Boolean(), nullable=True),
        sa.Column('review_reason', sa.String(length=200), nullable=True),
        sa.Column('erp_created', sa.Boolean(), nullable=True),
        sa.Column('erp_order_id', sa.String(length=100), nullable=True),
        sa.Column('validated_by_human', sa.String(length=100), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['call_id'], ['calls.id'], ),
        sa.ForeignKeyConstraint(['pharmacy_id'], ['pharmacies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_order_id', 'orders', ['order_id'], unique=True)

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('audio_transcript', sa.Text(), nullable=True),
        sa.Column('quantity_asked', sa.Integer(), nullable=False),
        sa.Column('quantity_unit', sa.String(length=20), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('line_total', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('extracted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('order_items')
    op.drop_index('ix_orders_order_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_calls_call_id', table_name='calls')
    op.drop_table('calls')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_index('ix_products_cip13', table_name='products')
    op.drop_table('products')
    op.drop_index('ix_pharmacies_phone_number', table_name='pharmacies')
    op.drop_index('ix_pharmacies_pharmacy_id', table_name='pharmacies')
    op.drop_table('pharmacies')
