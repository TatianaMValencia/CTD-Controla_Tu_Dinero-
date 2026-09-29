from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.finance import Account, Category, Transaction
from app.models.user import User
from app.services.calculos import balance_mes, saldo_actual, tasa_ahorro

router = APIRouter(tags=["resumen"])


@router.get("/resumen")
def resumen(mes: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ing = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter(
        Transaction.user_id == user.id, Transaction.tipo == "ingreso",
        func.to_char(Transaction.fecha, "YYYY-MM") == mes).scalar() or 0)
    gas = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter(
        Transaction.user_id == user.id, Transaction.tipo == "gasto",
        func.to_char(Transaction.fecha, "YYYY-MM") == mes).scalar() or 0)
    bal = balance_mes(ing, gas)
    por_cuenta = []
    for a in db.query(Account).filter_by(user_id=user.id).all():
        ai = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter(
            Transaction.cuenta_id == a.id, Transaction.tipo == "ingreso",
            func.to_char(Transaction.fecha, "YYYY-MM") == mes).scalar() or 0)
        ag = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter(
            Transaction.cuenta_id == a.id, Transaction.tipo == "gasto",
            func.to_char(Transaction.fecha, "YYYY-MM") == mes).scalar() or 0)
        gi = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter_by(cuenta_id=a.id, tipo="ingreso").scalar() or 0)
        gg = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter_by(cuenta_id=a.id, tipo="gasto").scalar() or 0)
        por_cuenta.append({"cuenta_id": a.id, "nombre": a.nombre, "ingresos": ai, "gastos": ag,
                           "saldo_actual": saldo_actual(float(a.saldo_inicial), gi, gg)})
    return {"mes": mes, "ingresos": ing, "gastos": gas, "balance_mes": bal,
            "ahorro": bal, "tasa_ahorro": tasa_ahorro(ing, bal), "por_cuenta": por_cuenta,
            "mensaje": f"Gastaste {gas} de {ing}. Balance {bal}."}


@router.get("/reportes/evolucion")
def evolucion(meses: int = 6, hasta: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from datetime import date as _date

    meses = max(1, min(meses, 12))
    if hasta:
        try:
            y, m = map(int, hasta.split("-"))
        except Exception:
            raise HTTPException(422, "hasta debe ser YYYY-MM")
    else:
        hoy = _date.today()
        y, m = hoy.year, hoy.month
    nombres = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
               "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    items = []
    for i in range(meses - 1, -1, -1):
        yy, mm = y, m - i
        while mm <= 0:
            mm += 12
            yy -= 1
        key = f"{yy:04d}-{mm:02d}"
        ing = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter(
            Transaction.user_id == user.id, Transaction.tipo == "ingreso",
            func.to_char(Transaction.fecha, "YYYY-MM") == key).scalar() or 0)
        gas = float(db.query(func.coalesce(func.sum(Transaction.monto), 0)).filter(
            Transaction.user_id == user.id, Transaction.tipo == "gasto",
            func.to_char(Transaction.fecha, "YYYY-MM") == key).scalar() or 0)
        items.append({"mes": key, "ingresos": ing, "gastos": gas, "balance_mes": balance_mes(ing, gas)})
    if len(items) >= 2 and items[-2]["ingresos"] > 0:
        pct = round((items[-1]["ingresos"] - items[-2]["ingresos"]) / items[-2]["ingresos"] * 100)
        ult, prev = items[-1]["mes"], items[-2]["mes"]
        un, pn = nombres[int(ult.split("-")[1])], nombres[int(prev.split("-")[1])]
        palabra = "más" if pct >= 0 else "menos"
        mensaje = f"En {un} ingresaste {abs(pct)}% {palabra} que en {pn}."
    elif len(items) >= 2:
        un = nombres[int(items[-1]["mes"].split("-")[1])]
        mensaje = f"En {un} no hubo ingresos el mes anterior para comparar."
    else:
        mensaje = "Sin datos suficientes."
    return {"items": items, "mensaje": mensaje}


@router.get("/reportes/distribucion")
def distribucion(desde: str | None = None, hasta: str | None = None, tipo: str = "gasto",
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Transaction.categoria_id, func.coalesce(func.sum(Transaction.monto), 0)).filter(
        Transaction.user_id == user.id, Transaction.tipo == tipo)
    if desde:
        q = q.filter(Transaction.fecha >= desde)
    if hasta:
        q = q.filter(Transaction.fecha <= hasta)
    rows = q.group_by(Transaction.categoria_id).all()
    total = sum(float(t) for _, t in rows) or 0
    out = []
    for cat_id, s in rows:
        cat = db.get(Category, cat_id) if cat_id else None
        st = float(s)
        out.append({"categoria_id": cat_id, "nombre": cat.nombre if cat else "Sin categoría",
                    "total": st, "porcentaje": round(st / total * 100, 2) if total else 0})
    return sorted(out, key=lambda x: x["total"], reverse=True)


@router.get("/simulador")
def simulador_stub():
    return {"code": "NOT_IMPLEMENTED", "detail": "¿Puedo permitírmelo? es Fase 2"}, 501
