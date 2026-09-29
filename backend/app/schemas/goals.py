from datetime import date

from pydantic import BaseModel, Field


class MetaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    objetivo: float = Field(gt=0)
    fecha_objetivo: date | None = None
    imagen_url: str | None = None


class MetaPatch(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    objetivo: float | None = Field(default=None, gt=0)
    fecha_objetivo: date | None = None
    imagen_url: str | None = None


class AporteIn(BaseModel):
    monto: float = Field(gt=0)
    fecha: date | None = None


class MetaOut(BaseModel):
    id: str
    nombre: str
    objetivo: float
    ahorrado: float
    faltante: float
    porcentaje: float
    excedente: float
    meses_restantes: int | None
    ahorro_requerido_mensual: float | None
    estado: str
    vencida: bool
    imagen_url: str | None = None
