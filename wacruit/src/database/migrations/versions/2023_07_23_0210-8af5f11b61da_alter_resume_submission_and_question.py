"""Alter resume and recruiting column type
alter resume question contents from String(10000), nullable to Text, non-nullable
alter resume submission answer from String(10000), nullable to Text, non-nullable
alter recruiting description from String(10000), nullable to Text, non-nullable

Revision ID: 8af5f11b61da
Revises: 51ee6d9fff87
Create Date: 2023-07-23 02:10:12.854814

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "8af5f11b61da"
down_revision = "51ee6d9fff87"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "resume_question",
        "content",
        existing_type=mysql.VARCHAR(length=10000),
        type_=sa.Text(),
        nullable=False,
    )
    op.alter_column(
        "resume_submission",
        "answer",
        existing_type=mysql.VARCHAR(length=10000),
        type_=sa.Text(),
        nullable=False,
    )
    op.alter_column(
        "recruiting",
        "description",
        existing_type=mysql.VARCHAR(length=10000),
        type_=sa.Text(),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "resume_submission",
        "answer",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=10000),
        nullable=True,
    )
    op.alter_column(
        "resume_question",
        "content",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=10000),
        nullable=True,
    )
    op.alter_column(
        "recruiting",
        "description",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=10000),
        nullable=True,
    )
    # ### end Alembic commands ###
