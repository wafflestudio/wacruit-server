"""add source code column to code_submission

Revision ID: cc8ee03dfd6e
Revises: 101ccb508ee1
Create Date: 2024-08-12 00:17:11.325129

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "cc8ee03dfd6e"
down_revision = "101ccb508ee1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("code_submission", sa.Column("source_code", sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("code_submission", "source_code")
    # ### end Alembic commands ###
