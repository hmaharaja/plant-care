"""convert enum values to uppercase

Revision ID: 1e4934a3978b
Revises: 2be105a5fba8
Create Date: 2026-03-28 16:04:23.053761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e4934a3978b'
down_revision: Union[str, Sequence[str], None] = '2be105a5fba8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL doesn't support ALTER TYPE ... RENAME VALUE, so we need to:
    # 1. Add new uppercase values to the enum (must commit before using)
    # 2. Update existing data to uppercase
    # 3. Drop old lowercase values

    # Step 1: Add new enum values (PostgreSQL allows adding new values)
    op.execute("ALTER TYPE lightrequirement ADD VALUE IF NOT EXISTS 'LOW'")
    op.execute("ALTER TYPE lightrequirement ADD VALUE IF NOT EXISTS 'MEDIUM'")
    op.execute("ALTER TYPE lightrequirement ADD VALUE IF NOT EXISTS 'BRIGHT_INDIRECT'")
    op.execute("ALTER TYPE lightrequirement ADD VALUE IF NOT EXISTS 'FULL_SUN'")

    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'SANDY'")
    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'LOAM'")
    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'CLAY'")
    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'PEAT'")
    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'WELL_DRAINING'")
    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'WELL_DRAINING_AERATED'")
    op.execute("ALTER TYPE soilcondition ADD VALUE IF NOT EXISTS 'CACTI'")

    # Step 2: Use a transaction to ensure enum changes are committed before updating
    # By using execute with a transaction, we force a commit of the ALTER TYPE first
    conn = op.get_bind().connection
    # Execute update in a way that ensures the ALTER TYPE changes are visible
    conn.commit()

    # Now update existing data from lowercase to uppercase
    op.execute("UPDATE care_templates SET light_requirements = 'LOW' WHERE light_requirements = 'low'")
    op.execute("UPDATE care_templates SET light_requirements = 'MEDIUM' WHERE light_requirements = 'medium'")
    op.execute("UPDATE care_templates SET light_requirements = 'BRIGHT_INDIRECT' WHERE light_requirements = 'bright_indirect'")
    op.execute("UPDATE care_templates SET light_requirements = 'FULL_SUN' WHERE light_requirements = 'full_sun'")

    op.execute("UPDATE care_templates SET soil_conditions = 'SANDY' WHERE soil_conditions = 'sandy'")
    op.execute("UPDATE care_templates SET soil_conditions = 'LOAM' WHERE soil_conditions = 'loam'")
    op.execute("UPDATE care_templates SET soil_conditions = 'CLAY' WHERE soil_conditions = 'clay'")
    op.execute("UPDATE care_templates SET soil_conditions = 'PEAT' WHERE soil_conditions = 'peat'")
    op.execute("UPDATE care_templates SET soil_conditions = 'WELL_DRAINING' WHERE soil_conditions = 'well_draining'")
    op.execute("UPDATE care_templates SET soil_conditions = 'WELL_DRAINING_AERATED' WHERE soil_conditions = 'well_draining_aerated'")
    op.execute("UPDATE care_templates SET soil_conditions = 'CACTI' WHERE soil_conditions = 'cacti'")


def downgrade() -> None:
    """Downgrade schema."""
    # Convert back to lowercase
    op.execute("UPDATE care_templates SET light_requirements = 'low' WHERE light_requirements = 'LOW'")
    op.execute("UPDATE care_templates SET light_requirements = 'medium' WHERE light_requirements = 'MEDIUM'")
    op.execute("UPDATE care_templates SET light_requirements = 'bright_indirect' WHERE light_requirements = 'BRIGHT_INDIRECT'")
    op.execute("UPDATE care_templates SET light_requirements = 'full_sun' WHERE light_requirements = 'FULL_SUN'")

    op.execute("UPDATE care_templates SET soil_conditions = 'sandy' WHERE soil_conditions = 'SANDY'")
    op.execute("UPDATE care_templates SET soil_conditions = 'loam' WHERE soil_conditions = 'LOAM'")
    op.execute("UPDATE care_templates SET soil_conditions = 'clay' WHERE soil_conditions = 'CLAY'")
    op.execute("UPDATE care_templates SET soil_conditions = 'peat' WHERE soil_conditions = 'PEAT'")
    op.execute("UPDATE care_templates SET soil_conditions = 'well_draining' WHERE soil_conditions = 'WELL_DRAINING'")
    op.execute("UPDATE care_templates SET soil_conditions = 'well_draining_aerated' WHERE soil_conditions = 'WELL_DRAINING_AERATED'")
    op.execute("UPDATE care_templates SET soil_conditions = 'cacti' WHERE soil_conditions = 'CACTI'")