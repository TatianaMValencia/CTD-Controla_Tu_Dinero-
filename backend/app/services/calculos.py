"""Fórmulas canónicas RC-01 a RC-05. Única fuente lógica (ver docs/api-contrato.md §1.1).

Puras y testeables: no tocan DB. Redondeo 2 decimales en borde API, aquí floats.
"""
from datetime import date


def r2(x: float) -> float:
    return round(float(x), 2)


# RC-01
def saldo_actual(saldo_inicial: float, ingresos: float, gastos: float) -> float:
    return r2(saldo_inicial + ingresos - gastos)


# RC-02
def balance_mes(ingresos_mes: float, gastos_mes: float) -> float:
    return r2(ingresos_mes - gastos_mes)


def tasa_ahorro(ingresos_mes: float, balance: float) -> float:
    if ingresos_mes <= 0:
        return 0.0
    return r2(balance / ingresos_mes * 100)


# RC-03
def presupuesto_restante(monto: float, gastado: float) -> float:
    return r2(monto - gastado)


def presupuesto_porcentaje(monto: float, gastado: float) -> float:
    if monto <= 0:
        return 0.0
    return r2(gastado / monto * 100)


def presupuesto_estado(porcentaje: float) -> str:
    if porcentaje < 80:
        return "ok"
    if porcentaje <= 100:
        return "alerta"
    return "excedido"


# RC-04
def meta_faltante(objetivo: float, ahorrado: float) -> float:
    return r2(max(objetivo - ahorrado, 0))


def meta_porcentaje(objetivo: float, ahorrado: float) -> float:
    if objetivo <= 0:
        return 0.0
    return r2(ahorrado / objetivo * 100)


def meta_excedente(objetivo: float, ahorrado: float) -> float:
    return r2(max(ahorrado - objetivo, 0))


# RC-05
def meses_restantes(fecha_objetivo: date | None, hoy: date) -> int | None:
    if fecha_objetivo is None:
        return None
    diff = (fecha_objetivo.year * 12 + fecha_objetivo.month) - (hoy.year * 12 + hoy.month) + 1
    return max(1, diff)


def ahorro_requerido_mensual(faltante: float, meses: int | None) -> float | None:
    if meses is None:
        return None
    if faltante <= 0:
        return 0.0
    return r2(faltante / meses)
