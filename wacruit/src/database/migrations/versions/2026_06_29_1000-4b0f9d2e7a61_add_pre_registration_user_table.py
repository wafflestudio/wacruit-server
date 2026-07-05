"""add pre_registration user table

Revision ID: 4b0f9d2e7a61
Revises: 8c4d2f1a6b7e
Create Date: 2026-06-29 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "4b0f9d2e7a61"
down_revision = "8c4d2f1a6b7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_registration_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pre_registration_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=30), nullable=False),
        sa.Column("university", sa.String(length=50), nullable=True),
        sa.Column("college", sa.String(length=50), nullable=True),
        sa.Column("department", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["pre_registration_id"],
            ["pre_registration.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "pre_registration_id",
            "email",
            name="uk_pre_registration_user_email",
        ),
    )


def downgrade() -> None:
    op.drop_table("pre_registration_user")
