"""0004 goals.imagen_url (data-URL para foto de meta).

Revision ID: 0004_goal_imagen
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_goal_imagen"
down_revision = "0003_password_codes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("goals", sa.Column("imagen_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("goals", "imagen_url")
