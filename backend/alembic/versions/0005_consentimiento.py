"""0005 consentimiento legal: términos y tratamiento de datos (Ley 1581/2012).

Revision ID: 0005_consentimiento
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_consentimiento"
down_revision = "0004_goal_imagen"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("acepta_terminos_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("terminos_version", sa.String(10), nullable=True))
    op.add_column("users", sa.Column("acepta_datos_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("datos_version", sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "datos_version")
    op.drop_column("users", "acepta_datos_at")
    op.drop_column("users", "terminos_version")
    op.drop_column("users", "acepta_terminos_at")
