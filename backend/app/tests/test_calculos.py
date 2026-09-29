from datetime import date

from app.services.calculos import (
    ahorro_requerido_mensual,
    balance_mes,
    meta_faltante,
    meses_restantes,
    presupuesto_porcentaje,
    presupuesto_restante,
    saldo_actual,
)


def test_rc01_saldo():
    assert saldo_actual(1000, 500, 200) == 1300


def test_rc02_balance():
    assert balance_mes(2500000, 1750000) == 750000


def test_rc03_presupuesto_negativo_y_mas100():
    assert presupuesto_restante(500000, 620000) == -120000
    assert presupuesto_porcentaje(500000, 620000) == 124.0


def test_rc04_meta_sobrecumplida():
    assert meta_faltante(500000, 650000) == 0
    assert ahorro_requerido_mensual(0, 4) == 0.0


def test_rc05_meses_inclusivos():
    hoy = date(2026, 9, 17)
    assert meses_restantes(date(2026, 12, 15), hoy) == 4
    assert meses_restantes(date(2026, 9, 30), hoy) == 1
    assert meses_restantes(None, hoy) is None
