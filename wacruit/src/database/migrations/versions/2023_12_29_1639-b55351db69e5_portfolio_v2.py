"""Portfolio v2

Revision ID: b55351db69e5
Revises: d8d10f453a15
Create Date: 2023-12-29 16:39:49.646726

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "b55351db69e5"
down_revision = "d8d10f453a15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "portfolio_file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recruiting_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["recruiting_id"], ["recruiting.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "portfolio_url", sa.Column("recruiting_id", sa.Integer(), nullable=False)
    )
    # 21.5기 디자이너 리크루팅 id가 2번임 (dev, prod 둘 다)
    op.execute("UPDATE portfolio_url SET recruiting_id = 2")
    op.create_foreign_key(
        "portfolio_url_ibfk_2",
        "portfolio_url",
        "recruiting",
        ["recruiting_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("portfolio_url_ibfk_1", "portfolio_url", type_="foreignkey")
    op.alter_column(
        "portfolio_url", "user_id", existing_type=mysql.INTEGER(), nullable=False
    )
    op.create_foreign_key(
        "portfolio_url_ibfk_1",
        "portfolio_url",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("portfolio_url_ibfk_1", "portfolio_url", type_="foreignkey")
    op.alter_column(
        "portfolio_url", "user_id", existing_type=mysql.INTEGER(), nullable=True
    )
    op.create_foreign_key(
        "portfolio_url_ibfk_1",
        "portfolio_url",
        "user",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint("portfolio_url_ibfk_2", "portfolio_url", type_="foreignkey")
    op.drop_column("portfolio_url", "recruiting_id")
    op.drop_table("portfolio_file")
    # ### end Alembic commands ###