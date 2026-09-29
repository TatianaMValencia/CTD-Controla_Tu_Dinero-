from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from app.models.base import UUIDBase


class User(UUIDBase):
    __tablename__ = "users"

    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    moneda: Mapped[str] = mapped_column(String(3), default="COP")
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_done: Mapped[bool] = mapped_column(Boolean, default=False)
    # Consentimiento legal (Ley 1581 de 2012). NULL = versión anterior, se pide al entrar.
    acepta_terminos_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    terminos_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
    acepta_datos_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    datos_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
