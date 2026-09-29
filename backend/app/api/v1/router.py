from fastapi import APIRouter

from app.api.v1 import auth, catalogos, cuentas, movimientos, plan, resumen

api_router = APIRouter()
for r in (auth.router, cuentas.router, movimientos.router, plan.router, resumen.router, catalogos.router):
    api_router.include_router(r)
