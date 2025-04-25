"""Add weight field to parts table

Revision ID: add_weight_to_parts
Create Date: 2023-07-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_weight_to_parts'
down_revision = '975d38bed1d7'  # Points to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Add weight column to parts table"""
    op.add_column('parts', sa.Column('weight', sa.Numeric(precision=10, scale=3), nullable=True))


def downgrade():
    """Remove weight column from parts table"""
    op.drop_column('parts', 'weight') 