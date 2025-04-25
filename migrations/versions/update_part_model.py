"""Update Part model with inventory and vehicle targeting fields

Revision ID: update_part_model
Create Date: 2023-11-15 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_part_model'
down_revision = 'add_weight_to_parts'  # Points to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Add new fields to parts table and remove weight field"""
    # Add new columns for vehicle targeting and inventory management
    op.add_column('parts', sa.Column('make', sa.String(100), nullable=True))
    op.add_column('parts', sa.Column('model', sa.String(100), nullable=True))
    op.add_column('parts', sa.Column('storage_location', sa.String(100), nullable=True))
    
    # Remove weight column
    op.drop_column('parts', 'weight')


def downgrade():
    """Restore to previous state: add weight field and remove new fields"""
    # Add back the weight column
    op.add_column('parts', sa.Column('weight', sa.Numeric(precision=10, scale=3), nullable=True))
    
    # Remove added columns
    op.drop_column('parts', 'make')
    op.drop_column('parts', 'model')
    op.drop_column('parts', 'storage_location') 