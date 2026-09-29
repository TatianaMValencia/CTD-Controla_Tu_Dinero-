from datetime import date

from pydantic import BaseModel, Field


class CuentaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    tipo: str = Field(default="efectivo", pattern="^(efectivo|banco|bolsa|otro)$")
    saldo_inicial: float = Field(default=0, ge=0)


class CuentaOut(CuentaIn):
    id: str
    saldo_actual: float


class CategoriaIn(BaseModel):
    nombre: str
    tipo: str = Field(pattern="^(ingreso|gasto|ambos)$")
    icono: str = "tag"


class MovimientoIn(BaseModel):
    tipo: str = Field(pattern="^(ingreso|gasto)$")
    monto: float = Field(gt=0)
    fecha: date
    descripcion: str = ""
    categoria_id: str | None = None
    cuenta_id: str
    metodo_id: str | None = None


class PresupuestoIn(BaseModel):
    categoria_id: str
    monto: float = Field(gt=0)
    periodo: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


class CuentaPatch(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    tipo: str | None = Field(default=None, pattern="^(efectivo|banco|bolsa|otro)$")
    saldo_inicial: float | None = Field(default=None, ge=0)


class CuentaDividirIn(BaseModel):
    origen_id: str
    nombre: str = Field(min_length=1, max_length=120)
    tipo: str = Field(default="banco", pattern="^(efectivo|banco|bolsa|otro)$")
    monto: float = Field(gt=0)


class MovimientoPatch(BaseModel):
    tipo: str | None = Field(default=None, pattern="^(ingreso|gasto)$")
    monto: float | None = Field(default=None, gt=0)
    fecha: date | None = None
    descripcion: str | None = None
    categoria_id: str | None = None
    cuenta_id: str | None = None
    metodo_id: str | None = None


class PresupuestoPatch(BaseModel):
    monto: float = Field(gt=0)


class CategoriaPatch(BaseModel):
    nombre: str | None = None
    icono: str | None = None
    activa: bool | None = None
