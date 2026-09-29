"""0001 initial: users, accounts, categories, methods, transactions, budgets, goals.

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("correo", sa.String(160), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="COP"),
    )
    op.create_index("ix_users_correo", "users", ["correo"])
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False, server_default="efectivo"),
        sa.Column("saldo_inicial", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False, server_default="gasto"),
        sa.Column("icono", sa.String(60), nullable=False, server_default="tag"),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default="true"),
        sa.UniqueConstraint("user_id", "nombre", "tipo", name="uq_cat_user_nombre_tipo"),
    )
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("nombre", sa.String(120), nullable=False),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("cuenta_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("categoria_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("metodo_id", sa.String(36), sa.ForeignKey("payment_methods.id"), nullable=True),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("monto", sa.Numeric(14, 2), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False, index=True),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
        sa.Column("idempotency_key", sa.String(36), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "budgets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("categoria_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("monto", sa.Numeric(14, 2), nullable=False),
        sa.Column("periodo", sa.String(7), nullable=False),
        sa.UniqueConstraint("user_id", "categoria_id", "periodo", name="uq_budget_user_cat_periodo"),
    )
    op.create_table(
        "goals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("objetivo", sa.Numeric(14, 2), nullable=False),
        sa.Column("fecha_objetivo", sa.Date(), nullable=True),
    )
    op.create_table(
        "goal_aportes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("goal_id", sa.String(36), sa.ForeignKey("goals.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("monto", sa.Numeric(14, 2), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("idempotency_key", sa.String(36), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "habits",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False, server_default=""),
    )
    op.create_table(
        "recurrings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    for t in ["recurrings", "habits", "goal_aportes", "goals", "budgets", "transactions", "payment_methods", "categories", "accounts"]:
        op.drop_table(t)
    op.drop_index("ix_users_correo", table_name="users")
    op.drop_table("users")
