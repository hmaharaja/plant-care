"""rename water_interval_days to default_watering_interval_days

Revision ID: 705c02fe189f
Revises: 11c63814d5e7
Create Date: 2026-03-24 14:28:04.673768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '705c02fe189f'
down_revision: Union[str, Sequence[str], None] = '11c63814d5e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('care_templates', 'watering_interval_days', new_column_name='default_watering_interval_days')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('care_templates', 'default_watering_interval_days', new_column_name='watering_interval_days')
