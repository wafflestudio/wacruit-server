"""Add pinned column to announcement

Revision ID: 5bbc8b8ae19c
Revises: 074873a1c19a
Create Date: 2023-08-05 14:47:29.231220

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5bbc8b8ae19c"
down_revision = "074873a1c19a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "announcement",
        sa.Column("pinned", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("announcement", "pinned")
    # ### end Alembic commands ###
