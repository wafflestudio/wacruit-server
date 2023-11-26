"""empty message

Revision ID: 2603f3af2e99
Revises: d8d10f453a15
Create Date: 2023-11-05 17:19:54.493755

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "2603f3af2e99"
down_revision = "d8d10f453a15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "portfolio_file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("is_uploaded", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column(
        "portfolio_url", sa.Column("generation", sa.String(length=255), nullable=True)
    )
    op.alter_column(
        "portfolio_url",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("portfolio_file")
    op.drop_column("portfolio_url", "generation")
    # ### end Alembic commands ###
