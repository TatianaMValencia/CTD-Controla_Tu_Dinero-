"""Metas (Opción A: solo seguimiento, RN-09) + tablas reservadas Fase 2."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class Goal(UUIDBase):
    __tablename__ = "goals"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    objetivo: Mapped[float] = mapped_column(Numeric(14, 2))
    fecha_objetivo: Mapped[date | None] = mapped_column(Date, nullable=True)
    imagen_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # data-URL (foto meta) o URL externa


class GoalAporte(UUIDBase):
    __tablename__ = "goal_aportes"

    goal_id: Mapped[str] = mapped_column(String(36), ForeignKey("goals.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    monto: Mapped[float] = mapped_column(Numeric(14, 2))
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    idempotency_key: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Habit(UUIDBase):
    """Reservada Fase 2, sin lógica MVP."""

    __tablename__ = "habits"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    nombre: Mapped[str] = mapped_column(String(120), default="")


class Recurring(UUIDBase):
    """Reservada Fase 2, sin lógica MVP."""

    __tablename__ = "recurrings"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    descripcion: Mapped[str] = mapped_column(Text, default="")
