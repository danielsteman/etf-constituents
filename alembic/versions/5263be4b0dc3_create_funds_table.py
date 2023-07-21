"""create funds table

Revision ID: 5263be4b0dc3
Revises:
Create Date: 2023-07-13 23:10:05.110173

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5263be4b0dc3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fundreference",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("fund_manager", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id_"),
    )
    op.create_table(
        "fundholdings",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("fund_name", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=255), nullable=False),
        sa.Column("instrument", sa.String(length=255), nullable=False),
        sa.Column("market_value", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("nominal_value", sa.Float(), nullable=False),
        sa.Column("nominal", sa.Float(), nullable=False),
        sa.Column("cusip", sa.String(length=255), nullable=True),
        sa.Column("isin", sa.String(length=255), nullable=False),
        sa.Column("sedol", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=False),
        sa.Column("currency", sa.String(length=255), nullable=False),
        sa.Column("exchange", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["fund_name"], ["fundreference.id_"]),
        sa.PrimaryKeyConstraint("id_"),
    )


def downgrade():
    op.drop_table("fundholdings")
    op.drop_table("fundreference")
