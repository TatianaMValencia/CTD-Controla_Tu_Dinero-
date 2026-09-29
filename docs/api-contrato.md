# Contrato API v1 — validable
Base: `http://localhost:8000/api/v1` · Stack referencia: FastAPI + PostgreSQL · Auth: JWT Bearer · Todo español en mensajes usuario.

## 1. Convenciones globales

- JSON `application/json; charset=utf-8`. Fechas `YYYY-MM-DD`, datetimes ISO8601 UTC. Montos `number` >0, 2 decimales (ej 25000.00). Moneda la del usuario (`COP, USD, MXN, EUR` MVP).
- Versionado URL `/api/v1`. Respuesta paginada: `GET` listados aceptan `?page=1&page_size=20&q=&orden=-fecha`.
  ```json
  { "items": [], "total": 0, "page": 1, "page_size": 20 }
  ```
- Errores estándar:
  ```json
  { "code": "VALIDATION_ERROR", "detail": "El monto debe ser mayor a 0", "field_errors": {"monto": "debe ser > 0"} }
  ```
  Códigos: `400 VALIDATION_ERROR`, `401 UNAUTHORIZED`, `403 FORBIDDEN`, `404 NOT_FOUND`, `409 CONFLICT` (duplicado/idempotencia), `422 UNPROCESSABLE`, `429 RATE_LIMITED`.
- Idempotencia (RN-08): `POST /movimientos` y `POST /metas/{id}/aportes` aceptan header `Idempotency-Key: <uuid>`. Reintento misma key+payload <24h → devuelve original `200`. Misma key distinto payload → `409`.
- Aislamiento: todo recurso filtra por `auth.user_id`. `403` si `user_id` ajeno.
- Health: `GET /health → {status: ok}` y `GET /api/v1/health → {db: ok}`.

## 1.1 Referencia canónica — fórmulas RC-01 a RC-05

> Único lugar de consulta para frontend, backend y pruebas automáticas. El backend es fuente de verdad; el frontend no recalcula para mostrar, solo replica para validación inmediata. Redondeo: 2 decimales. Montos siempre `>0` en entrada, cálculos pueden dar `0` o negativos donde se indica.

- **RC-01 `saldo_actual` (stock por cuenta):**
  `saldo_actual(cuenta) = saldo_inicial + SUM(movimientos ingreso cuenta, todo el histórico) − SUM(movimientos gasto cuenta, todo el histórico)`
  `disponible_total = SUM(saldo_actual todas las cuentas)`. Aportes a metas NO lo modifican (RN-09).
- **RC-02 `balance_mes` (flujo del mes):**
  `balance_mes = ingresos_mes − gastos_mes` (puede ser negativo). `tasa_ahorro = ingresos_mes>0 ? balance_mes/ingresos_mes×100 : 0`.
  No confundir con RC-01. Campo legacy `ahorro` = alias deprecated de `balance_mes`.
- **RC-03 cálculos de presupuesto (por categoría + periodo YYYY-MM):**
  `gastado = SUM(movimientos gasto, misma categoría, fecha en periodo)` · `restante = monto − gastado` (puede ser negativo) · `porcentaje_uso = monto>0 ? gastado/monto×100 : 0` (puede ser >100, UI capa barra a 100) · `estado = ok si <80, alerta si 80–100, excedido si >100` · `ritmo_diario = días_transcurridos>0 ? gastado/días_transcurridos : 0`.
- **RC-04 cálculos de meta (seguimiento, Opción A):**
  `ahorrado = SUM(aportes)` · `faltante = MAX(objetivo − ahorrado, 0)` · `porcentaje_meta = objetivo>0 ? ahorrado/objetivo×100 : 0` (puede ser >100) · `excedente = MAX(ahorrado − objetivo, 0)` · `estado = completada si ahorrado>=objetivo si no en_curso`.
- **RC-05 `meses_restantes` + requerido:**
  Si `fecha_objetivo IS NULL → meses_restantes=null, ahorro_requerido_mensual=null`.
  Si hay fecha: `meses_restantes = MAX(1, (año_obj×12+mes_obj) − (año_hoy×12+mes_hoy) + 1)` inclusivo por mes calendario. Si `fecha_objetivo<hoy y faltante>0 → vencida=true, meses_restantes=1`.
  `ahorro_requerido_mensual = meses_restantes IS NULL ? null : faltante/meses_restantes` (0 si faltante 0, etiqueta `estimación`).

## 2. Auth / Usuario (§15 Usuario)

### POST /auth/registro
Req: `{nombre, correo, password>=8, moneda: COP|USD|MXN|EUR}`
Res `201`: `{id, nombre, correo, moneda}` + crea seed: 3 cuentas? No, crea 1 cuenta `Efectivo`, 12 categorías, 3 métodos. Tokens aparte.
### POST /auth/login
Req: `{correo, password}` Res `200`: `{access_token, refresh_token, token_type: Bearer, expires_in: 1800}`
### POST /auth/refresh
Req: `{refresh_token}` Res `200` nuevo access.
### GET /auth/me (Bearer)
Res: `{id, nombre, correo, moneda, preferencias:{tema, inicio_semana}}`
### PATCH /auth/me
Req parcial `{nombre, moneda, preferencias}`. Cambiar moneda no reconvierte histórico (muestra nota `estimación`).

## 3. Cuentas ` /cuentas`

Model: `{id, nombre, tipo: efectivo|banco|bolsa|otro, saldo_inicial, saldo_actual(calculado), created_at}`
- `GET /cuentas → [{...}]` incluye RC-01: `saldo_actual = saldo_inicial + SUM(ingresos históricos cuenta) − SUM(gastos históricos cuenta)`. Total disponible = SUM saldos. Los aportes a metas NO afectan este cálculo (RN-09).
- `POST /cuentas ` Req `{nombre, tipo, saldo_inicial>=0}` `201`
- `PATCH /cuentas/{id}` `{nombre, tipo}` (no editar saldo_inicial si tiene movimientos → `409` con hint crear ajuste).
- `DELETE /cuentas/{id}` solo si `saldo_actual==0` y 0 movimientos, si no `409 {detail: Transfiere o elimina movimientos primero}`.

## 4. Categorías ` /categorias` + Métodos ` /metodos-pago`

Categoría: `{id, nombre, tipo: ingreso|gasto|ambos, icono: string, activa: bool}`
- `GET /categorias?tipo=gasto&solo_activas=true`
- `POST /categorias {nombre, tipo, icono}` `201`. Nombre único por usuario+tipo → `409`.
- `PATCH /categorias/{id} {nombre, icono, activa}`. Desactivar (`activa=false`) conserva historial RN-04.
- `DELETE` → solo si 0 movimientos, si no pedir desactivar (`409`).
Método: `{id, nombre}` — `GET, POST {nombre único}, PATCH, DELETE` misma regla. Seed: `Efectivo, Tarjeta, Transferencia`.

## 5. Movimientos ` /movimientos` (núcleo MVP-01/04)

Model: `{id, tipo: ingreso|gasto, monto, fecha: YYYY-MM-DD, descripcion, categoria_id, cuenta_id, metodo_id, created_at}`
Validación RN-03: `monto>0`, `fecha` válida, no futura >+1 día. `categoria.tipo` debe admitir `tipo` movimiento. `cuenta/metodo` propios.

- `POST /movimientos` + `Idempotency-Key`
  ```json
  // req
  {"tipo":"gasto","monto":45000,"fecha":"2026-09-16","descripcion":"Mercado","categoria_id":"uuid","cuenta_id":"uuid","metodo_id":"uuid"}
  // res 201
  {"id":"uuid", ...mismo, "saldo_cuenta_nuevo": 955000}
  ```
  Efecto: recalcula `saldo_actual`, invalida caché resumen/presupuesto. Si deja cuenta negativa: `201` + `warning: Deja la cuenta en -5000`.
- `GET /movimientos?tipo=&cuenta_id=&categoria_id=&desde=2026-09-01&hasta=2026-09-30&q=mercado&page=&page_size=` → paginado `orden=-fecha`.
- `GET /movimientos/{id}`, `PATCH /movimientos/{id}` (recalcula saldos), `DELETE /movimientos/{id} 204` (revierte saldo).

Flujo §11.1 validable: POST → GET /resumen + GET /presupuestos cambian sin acción extra.

## 6. Presupuestos ` /presupuestos` (MVP-06)

Model: `{id, categoria_id, monto, periodo: YYYY-MM (único por categoría), gastado(calc), restante(calc), porcentaje_uso, ritmo_diario, estado: ok|alerta|excedido}`
Cálculo servidor RN-05 + RC-03:
- `gastado = SUM(movimientos gasto misma categoria, fecha en periodo)`.
- `restante = monto − gastado` (puede ser negativo, no truncar).
- `porcentaje_uso = gastado/monto×100` (puede ser >100, frontend capa barra a 100).
- `estado = ok si <80, alerta si 80–100, excedido si >100`.

- `POST /presupuestos {categoria_id (tipo gasto), monto>0, periodo}` → `409` si ya existe.
- `GET /presupuestos?periodo=2026-09` → lista con cálculos + `dias_transcurridos, dias_periodo`.
  ```json
  {"id":"...","categoria":{"id":"...","nombre":"Comida"},"monto":500000,"periodo":"2026-09","gastado":320000,"restante":180000,"porcentaje_uso":64,"ritmo_diario":20000,"estado":"ok","mensaje":"Vas bien: te quedan 180000 de 500000."}
  ```
- `PATCH /presupuestos/{id} {monto}`, `DELETE 204`.

## 7. Metas + aportes (MVP-07, Opción A: solo seguimiento)

> Decisión MVP: el aporte NO es movimiento financiero. `POST /metas/{id}/aportes` NO crea transacción, NO modifica `saldo_actual`, NO entra en `/resumen`. El `ahorrado` está incluido dentro del disponible de cuentas. Ej: cuenta $2.000.000 + meta $500.000 ahorrados → los $500.000 siguen dentro de los $2.000.000. UI debe explicarlo. Opción B (descontar de cuenta) es Fase 2+.

Meta: `{id, nombre, objetivo>0, fecha_objetivo: YYYY-MM-DD|null, ahorrado(calc SUM aportes), faltante, porcentaje, excedente, meses_restantes, ahorro_requerido_mensual(estimación), estado: en_curso|completada, vencida: bool}`
Cálculos RC-04/RC-05:
- `ahorrado = SUM(aportes)`. `faltante = MAX(objetivo − ahorrado, 0)`.
- `porcentaje = ahorrado/objetivo×100` (puede >100). `excedente = MAX(ahorrado − objetivo, 0)`.
- `meses_restantes = null si fecha null; si no MAX(1, (año_obj×12+mes_obj)−(año_hoy×12+mes_hoy)+1)`. Si `fecha<hoy y faltante>0 → vencida=true, meses=1`.
- `ahorro_requerido_mensual = null si meses null; si no faltante/meses` (0 si faltante 0). Etiqueta `estimación`.
- `estado = completada si ahorrado>=objetivo si no en_curso`.
- `POST /metas {nombre, objetivo, fecha_objetivo}` `201`
- `GET /metas → [...]` con `ahorrado, faltante=MAX(objetivo−ahorrado,0), excedente, mensaje: Te faltan X, ahorra Y por mes (estimación). Si sobrecumplida: ¡Meta cumplida! Excedente X. Si sin fecha: Sin fecha, aporta a tu ritmo.`
- `POST /metas/{id}/aportes {monto>0, fecha} + Idempotency-Key → 201 {id, nuevo_ahorrado, nuevo_porcentaje, nuevo_faltante}`. NO toca cuentas/resumen (test obligatorio).
- `GET /metas/{id}/aportes` historial RN-06. `DELETE /metas/{id}/aportes/{aporte_id}` resta.
- `PATCH /metas/{id}`, `DELETE /metas/{id}` con `?confirm=true`.

## 8. Resumen + Reportes (MVP-05/08)

### GET /resumen?mes=2026-09
RC-01 + RC-02: `balance_mes = ingresos_mes − gastos_mes` (renombra al antiguo `ahorro`; se mantiene alias `ahorro` deprecated por compatibilidad hasta v1 final). `tasa_ahorro = ingresos>0 ? balance_mes/ingresos×100 : 0`. `saldo_actual` por cuenta es stock histórico, no se filtra por mes.
```json
{
  "mes":"2026-09","ingresos":2500000,"gastos":1750000,"balance_mes":750000,"ahorro":750000,"tasa_ahorro":30,
  "por_cuenta":[{"cuenta_id":"...","nombre":"Efectivo","ingresos":500000,"gastos":200000,"saldo_actual":800000}],
  "top_categorias_gasto":[{"categoria":"Comida","total":320000}],
  "mensaje": "Gastaste 1750000 de 2500000. Balance 750000 (30%)."
}
```
### GET /reportes/distribucion?desde=&hasta=&tipo=gasto → `[{categoria_id, nombre, total, porcentaje}]`
### GET /reportes/evolucion?meses=6 → `[{mes, ingresos, gastos, balance_mes}]` + `mensaje` 1 frase (principio §7: sin tecnicismos).
Fase 2 stub (devolver `501 NOT_IMPLEMENTED` con `detail`): `/simulador`, `/pronostico`, `/escenarios`.

## 9. Respaldo (MVP-10)

- `GET /respaldo/export?formato=json|csv` → `200` archivo. JSON: `{version:1, exported_at, usuario, cuentas, categorias, metodos, movimientos, presupuestos, metas+aportes}`.
- `POST /respaldo/import` body JSON mismo schema, `?modo=reemplazar|agregar`. Valida RN-03, reporta `{creados, omitidos_duplicados, errores[]}`. Límite 5MB MVP.
- Frontend botón Config → Respaldo: Exportar 1 clic + Importar con confirmación.

## 10. Códigos y validación cruzada frontend

Backend es fuente verdad. Frontend replica mensajes: monto, fecha, categoría/cuenta requeridas. `422` muestra `field_errors` junto al input. `401` → refresh o login. `409 duplicado` → “Ya registraste esto, revisa historial” (RN-08).

## 11. Checklist validación API

- [ ] Registro→login→me ok, seed creado.
- [ ] POST movimiento actualiza GET /cuentas y GET /resumen.balance_mes.
- [ ] POST movimiento misma Idempotency-Key no duplica.
- [ ] GET /presupuestos?periodo cuadra con SUM manual; restante negativo y % >100 visibles.
- [ ] POST aporte actualiza faltante MAX(...,0); NO cambia saldos ni resumen (RN-09).
- [ ] Meta sobrecumplida: faltante 0, excedente>0, requerido 0, estado completada.
- [ ] Meta sin fecha: meses null, requerido null. Meta vencida: vencida true, meses 1.
- [ ] Export JSON reimportado en user limpio da mismos totales.
- [ ] Rutas fase2 devuelven 501 con mensaje claro, no 500.

---
Implementar en este orden: auth → cuentas/categorías/métodos → movimientos → presupuestos → metas → resumen/reportes → respaldo.
