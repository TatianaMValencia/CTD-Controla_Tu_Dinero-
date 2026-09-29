"""0002 2FA email + onboarding.

Revision ID: 0002_2fa_onboarding
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_2fa_onboarding"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_2fa_enabled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("onboarding_done", sa.Boolean(), nullable=False, server_default="false"))
    op.create_table(
        "two_fa_codes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_table("two_fa_codes")
    op.drop_column("users", "onboarding_done")
    op.drop_column("users", "is_2fa_enabled")
