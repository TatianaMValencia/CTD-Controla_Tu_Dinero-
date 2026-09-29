from typing import Annotated

from pydantic import BaseModel, BeforeValidator, EmailStr, Field


def _norm_correo(v):
    # Teclados móviles agregan espacios/mayúsculas: normalizar antes de validar.
    return v.strip().lower() if isinstance(v, str) else v


CorreoLimpio = Annotated[EmailStr, BeforeValidator(_norm_correo)]


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    correo: CorreoLimpio
    password: str = Field(min_length=8)
    moneda: str = Field(default="COP", pattern="^(COP|USD|MXN|EUR)$")
    acepta_terminos: bool = False
    acepta_datos: bool = False


class LoginIn(BaseModel):
    correo: CorreoLimpio
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str = "Bearer"
    expires_in: int = 1800


class RefreshIn(BaseModel):
    refresh_token: str


class UserPatch(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    moneda: str | None = Field(default=None, pattern="^(COP|USD|MXN|EUR)$")


class LoginOut(BaseModel):
    requires_2fa: bool = False
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "Bearer"
    expires_in: int = 1800


class TwoFaSolicitarIn(BaseModel):
    correo: CorreoLimpio


class TwoFaVerificarIn(BaseModel):
    correo: CorreoLimpio
    code: str = Field(min_length=6, max_length=6, pattern="^[0-9]{6}$")


class TwoFaActivarIn(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern="^[0-9]{6}$")


class OnboardingCuentaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    tipo: str = Field(default="efectivo", pattern="^(efectivo|banco|bolsa|otro)$")
    monto: float = Field(ge=0)

class OnboardingIn(BaseModel):
    modo: str = Field(pattern="^(todo_junto|separadas)$")
    total: float = Field(ge=0)
    cuentas: list[OnboardingCuentaIn] = []


class CorreoCambiarIn(BaseModel):
    nuevo_correo: CorreoLimpio
    password: str = Field(min_length=1)


class PasswordSolicitarIn(BaseModel):
    correo: CorreoLimpio


class PasswordConfirmarIn(BaseModel):
    correo: CorreoLimpio
    code: str = Field(min_length=10, max_length=10, pattern="^[0-9]{10}$")
    nueva_password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: str
    nombre: str
    correo: str
    moneda: str
    onboarding_done: bool = False
    is_2fa_enabled: bool = False
    acepta_terminos: bool = False
    acepta_datos: bool = False


def user_out(user) -> UserOut:
    return UserOut(id=user.id, nombre=user.nombre, correo=user.correo, moneda=user.moneda,
                   onboarding_done=user.onboarding_done, is_2fa_enabled=user.is_2fa_enabled,
                   acepta_terminos=user.acepta_terminos_at is not None,
                   acepta_datos=user.acepta_datos_at is not None)


class ConsentimientoIn(BaseModel):
    acepta_terminos: bool = False
    acepta_datos: bool = False
