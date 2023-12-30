"""add short_description to recruiting

Revision ID: afea36c96c65
Revises: b55351db69e5
Create Date: 2023-12-30 23:12:24.399405

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "afea36c96c65"
down_revision = "b55351db69e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "recruiting",
        sa.Column("short_description", sa.String(length=255), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("recruiting", "short_description")
    # ### end Alembic commands ###
