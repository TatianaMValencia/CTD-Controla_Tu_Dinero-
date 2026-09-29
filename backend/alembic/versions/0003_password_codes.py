"""0003 password_codes para cambio de contraseña con código de 10 dígitos.

Revision ID: 0003_password_codes
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_password_codes"
down_revision = "0002_2fa_onboarding"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_codes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_table("password_codes")
