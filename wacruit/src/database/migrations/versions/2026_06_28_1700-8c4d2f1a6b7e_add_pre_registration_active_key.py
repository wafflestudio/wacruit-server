"""add pre_registration active key

Revision ID: 8c4d2f1a6b7e
Revises: 2f9c8e0a1b34
Create Date: 2026-06-28 17:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8c4d2f1a6b7e"
down_revision = "2f9c8e0a1b34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pre_registration",
        sa.Column("active_key", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        UPDATE pre_registration
        SET active_key = 1
        WHERE is_active = true
        ORDER BY id DESC
        LIMIT 1
        """
    )
    op.execute(
        """
        UPDATE pre_registration
        SET is_active = false
        WHERE active_key IS NULL AND is_active = true
        """
    )
    op.create_check_constraint(
        "ck_pre_registration_active_key",
        "pre_registration",
        "active_key IS NULL OR active_key = 1",
    )
    op.create_unique_constraint(
        "uk_pre_registration_active",
        "pre_registration",
        ["active_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uk_pre_registration_active",
        "pre_registration",
        type_="unique",
    )
    op.drop_constraint(
        "ck_pre_registration_active_key",
        "pre_registration",
        type_="check",
    )
    op.drop_column("pre_registration", "active_key")
