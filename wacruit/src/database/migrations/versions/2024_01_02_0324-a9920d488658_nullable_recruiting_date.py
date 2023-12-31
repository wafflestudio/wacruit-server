"""Modify recruiting table to allow null values for from_date and to_date

Revision ID: a9920d488658
Revises: afea36c96c65
Create Date: 2024-01-02 03:24:25.289451

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "a9920d488658"
down_revision = "afea36c96c65"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "recruiting", "from_date", existing_type=mysql.DATETIME(), nullable=True
    )
    op.alter_column(
        "recruiting", "to_date", existing_type=mysql.DATETIME(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "recruiting", "to_date", existing_type=mysql.DATETIME(), nullable=False
    )
    op.alter_column(
        "recruiting", "from_date", existing_type=mysql.DATETIME(), nullable=False
    )
    # ### end Alembic commands ###
