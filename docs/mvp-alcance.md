# MVP — Alcance validable
PWA Finanzas Personales · Concepto v1.0 Septiembre 2026 · Este doc congela qué entra al MVP y qué no.

> Lema: “Registra. Entiende. Decide. Avanza.” — Principio rector §7: claridad antes que cantidad, cada gráfico responde una pregunta o apoya una acción.

## 1. Objetivo del MVP

Demostrar el valor principal: una persona crea su cuenta, registra ingresos/gastos, entiende su disponible, crea al menos 1 presupuesto o meta, y recibe una explicación sencilla sin herramientas externas (§21).

Cadena MVP: `REGISTRAR → ORGANIZAR → ENTENDER (básico) → PLANEAR (básico)`. `DECIDIR/AVANZAR` avanzado (simulador, pronóstico, escenarios) es Fase 2+.

## 2. Dentro del alcance (10 compromisos §9)

| ID | Compromiso | Criterio de aceptación verificable |
|----|------------|-------------------------------------|
| MVP-01 | Registro ingresos/gastos con descripción, monto, fecha, categoría | Form `Nuevo movimiento` < 5 campos obligatorios: tipo, monto>0, fecha válida ≤ hoy+1 día, categoría, cuenta. Guarda en <2s, actualiza saldo + presupuesto + resumen sin recargar. Historia §11.1 |
| MVP-02 | Gestión categorías y métodos de pago | CRUD categorías (nombre, tipo ingreso/gasto/ambos, icono, activa/inactiva). CRUD métodos (efectivo, tarjeta, transferencia + personalizados). Desactivar no borra historial (RN-04). Seed inicial: ~12 categorías + 3 métodos |
| MVP-03 | Cuentas / bolsas (efectivo, bancos, otros) | CRUD cuentas (nombre, tipo, saldo_inicial). RC-01: `saldo_actual = saldo_inicial + SUM(ingresos históricos) − SUM(gastos históricos)` por cuenta; `disponible_total = SUM(saldo_actual)`. Eliminar solo si saldo 0 y sin movimientos, o exige transferir |
| MVP-04 | Historial con búsqueda y filtros básicos | Lista paginada (20/pág), filtros: texto `q`, tipo, cuenta, categoría, rango fechas. Orden fecha desc. Editar/eliminar con confirmación |
| MVP-05 | Resumen mensual | `GET /resumen?mes=YYYY-MM` → ingresos_mes, gastos_mes, `balance_mes = ingresos_mes − gastos_mes` (antes llamado `ahorro_mes`, se renombra por semántica), por cuenta y total. Texto auto: “Gastaste X de Y ingresado. Balance Z.” Ver RC-02 |
| MVP-06 | Presupuestos por categoría y periodo | Crear (categoría gasto, monto>0, periodo YYYY-MM). RC-03: `gastado`, `restante = monto − gastado` (puede ser negativo), `porcentaje_uso = gastado/monto×100` (puede ser >100), `ritmo_diario = gastado/días_transcurridos`. Estados: `ok <80`, `alerta 80–100`, `excedido >100` |
| MVP-07 | Metas de ahorro con progreso y faltante (seguimiento, Opción A) | Crear (nombre, objetivo>0, fecha_objetivo futura opcional). RC-04 + RC-05: aporte = solo seguimiento, NO movimiento, NO toca saldos. `ahorrado = SUM(aportes)`, `faltante = MAX(objetivo − ahorrado, 0)`, `porcentaje = ahorrado/objetivo×100` (puede ser >100, barra cap 100), `ahorro_requerido_mensual = faltante/meses_restantes`. Sobrecumplida → `faltante 0`, `excedente = ahorrado − objetivo` |
| MVP-08 | Vista Inicio centro de control | No es menú. Muestra: disponible total (SUM saldos), ingresos/gastos/balance del mes, 3 presupuestos en riesgo, 2 metas con progreso, próximos compromisos manuales (stub), FAB `+ Nuevo` siempre visible. Cada tarjeta con 1 frase explicativa (§12). Vocabulario UI: “disponible” = saldos, “balance del mes” = flujo mensual, “por ahorrar” = faltante metas |
| MVP-09 | PWA instalable + responsive | `manifest.webmanifest`, icons 192/512, theme-color, service-worker app-shell, funciona lectura sin conexión (offline básico). Layouts: móvil BottomNav 5 zonas, escritorio Sidebar. Responsive 360px → 1280px |
| MVP-10 | Persistencia segura + respaldo/exportación | Auth JWT + hash bcrypt, datos por `user_id` aislados. Export JSON/CSV (movimientos, presupuestos, metas) en 1 clic + import JSON básico. Riesgo §20 pérdida datos |

## 3. Navegación MVP (§13)

5 zonas, mismas en móvil y escritorio:

1. **Inicio:** resumen, alertas, progreso, acciones rápidas
2. **Movimientos:** ingresos, gastos, cuentas, categorías, historial
3. **Planificación:** presupuestos, metas (+ Calendario/Hábitos como pantallas `Próximamente` vacías para reservar ruta)
4. **Análisis:** reportes básicos — distribución por categoría (dona) + evolución 6 meses (barras) + 1 frase por gráfico
5. **Configuración:** perfil, moneda (COP/USD/MXN/EUR inicial), categorías, métodos, cuentas, seguridad, respaldo

Rutas: `/inicio, /movimientos, /movimientos/nuevo, /plan/presupuestos, /plan/metas, /analisis, /config/*`

## 4. Reglas de negocio (§14) — obligatorias en backend

- RN-01: ingreso aumenta disponible cuenta seleccionada.
- RN-02: gasto reduce disponible (permite negativo pero advierte “deja cuenta en −X”).
- RN-03: todo movimiento exige `monto>0` y `fecha` válida ISO8601. Monto se guarda positivo + `tipo`.
- RN-04: desactivar categoría/método/cuenta no altera historial (`activa=false`, `ON DELETE RESTRICT/SET NULL`).
- RN-05: presupuesto = SUM(movimientos tipo gasto, misma categoría, fecha dentro periodo). Sin categoría comodín en MVP.
- RN-06: meta conserva `goal_aportes`; borrar aporte resta progreso, borrar meta exige confirmación.
- RN-07: todo cálculo predictivo se etiqueta `estimación`.
- RN-08: anti-doble-registro: `Idempotency-Key` UUID en POST movimientos/aportes; reintento <24h devuelve original (409 si difiere payload).
- RN-09 (Opción A MVP): un aporte a meta NO es un movimiento financiero. NO crea transacción, NO modifica `saldo_actual` de ninguna cuenta, NO entra al resumen. Es solo seguimiento. El `ahorrado` de metas está incluido dentro del disponible de cuentas (doble conteo intencional y explicado en UI).

### 4.1 Reglas de cálculo canónicas (misma numeración que `api-contrato.md §1.1`)

- RC-01 `saldo_actual` (stock por cuenta):
  - `saldo_actual(cuenta) = saldo_inicial + SUM(ingresos cuenta, todo el histórico) − SUM(gastos cuenta, todo el histórico)`.
  - `disponible_total = SUM(saldo_actual todas las cuentas)`.
  - UI: “disponible” siempre = saldos. Nunca mezclar con flujo mensual.
- RC-02 `balance_mes` (flujo del mes, renombra al antiguo `ahorro_mes`):
  - `balance_mes = ingresos_mes − gastos_mes` (puede ser negativo).
  - `tasa_ahorro = si ingresos_mes>0 entonces balance_mes/ingresos_mes×100 si no 0`.
  - UI: “balance del mes” siempre = flujo.
- RC-03 cálculos de presupuesto (por categoría + periodo YYYY-MM):
  - `gastado = SUM(movimientos tipo gasto, misma categoría, fecha dentro periodo)`.
  - `restante = monto − gastado` (puede ser negativo, mostrar en rojo, no truncar).
  - `porcentaje_uso = si monto>0 entonces gastado/monto×100 si no 0` (puede ser >100, barra cap 100 + texto “excedido en X”).
  - `estado = ok si <80, alerta si 80–100, excedido si >100`. `ritmo_diario = si días_transcurridos>0 entonces gastado/días_transcurridos si no 0`.
  - Ejemplo: monto 500000, gastado 620000 → restante −120000, 124%.
- RC-04 cálculos de meta (seguimiento, Opción A):
  - `ahorrado = SUM(aportes)`. `faltante = MAX(objetivo − ahorrado, 0)` (nunca negativo en UI/API).
  - `porcentaje_meta = si objetivo>0 entonces ahorrado/objetivo×100 si no 0` (puede ser >100).
  - `excedente = MAX(ahorrado − objetivo, 0)`. Estado: `en_curso si ahorrado<objetivo`, `completada si ahorrado>=objetivo`.
  - UI sobrecumplida: barra 100%, texto “¡Meta cumplida! Excedente X”, `faltante 0`, `ahorro_requerido_mensual 0`.
- RC-05 `meses_restantes` + requerido:
  - Si `fecha_objetivo IS NULL` → `meses_restantes = null`, `ahorro_requerido_mensual = null`, mensaje “Sin fecha: aporta a tu ritmo (estimación no disponible)”.
  - Si hay fecha: `meses_restantes = MAX(1, (año_obj×12+mes_obj) − (año_hoy×12+mes_hoy) + 1)` — conteo inclusivo por mes calendario. Si `fecha_objetivo < hoy` y `faltante>0` → `vencida=true`, `meses_restantes=1`, requerido = faltante (ponerse al día en 1 mes) + mensaje vencida.
  - `ahorro_requerido_mensual = si meses_restantes IS NULL entonces null si no faltante/meses_restantes` (redondeo 2 decimales, etiqueta `estimación`).
  - Ejemplos con hoy=2026-09-17: obj 500000, ahorrado 200000, faltante 300000, fecha 2026-12-15 → meses=4 → 75000/mes. Misma fecha 2026-09-30 → meses=1 → 300000. Sin fecha → null.

## 5. Datos mínimos (§15) + semántica aporte (decisión Opción A)

`users → accounts → categories → payment_methods → transactions → budgets → goals → goal_aportes`. Tablas `habits, recurrings` se crean vacías para no migrar después, sin UI funcional.

> Decisión cerrada: aporte = seguimiento. Ejemplo: Cuenta $2.000.000, Meta $500.000 ahorrados → esos $500.000 siguen incluidos dentro de los $2.000.000. No se descuentan. UI obligatoria en Metas: “Tus metas son seguimiento, no apartan dinero real de tus cuentas.” + advertencia informativa (no bloqueo) si `SUM(ahorrado metas en_curso) > disponible_total`: “Tus metas suman más que tu disponible”.
> Opción B (aporte = transferencia real con `cuenta_origen`) queda explícitamente para Fase 2+, requeriría `goal_aportes.cuenta_id + transactions` vinculadas.

Campos núcleo: ver `api-contrato.md §2`. Moneda a nivel usuario, montos con 2 decimales.

## 6. No funcionales mínimos (§16)

- Responsive + accesibilidad AA básico: foco visible, labels, contraste, botones ≥44px, mensajes error claros.
- PWA: instalable, app-shell offline lectura; escritura offline encola y sincroniza (1 cola simple IndexedDB).
- Auth: JWT access 30min + refresh 7d, bcrypt, rate-limit login.
- Validaciones frontend + backend idénticas, español cotidiano, sin tecnicismos.
- Backup desde día 1 (MVP-10).

## 7. Fuera de alcance explícito (§10 — no hacer en MVP)

`¿Puedo permitírmelo?`, pronóstico ahorro, ritmo recomendado inteligente, detección cambios vs periodos, recordatorios push, escenarios “qué pasa si”, importación CSV bancaria automática, multi-moneda por movimiento, cuentas compartidas, gráficas avanzadas. Si aparece en revisión, mover a `backlog-fase2.md`.

## 8. Criterio de éxito (§21) — checklist de validación

- [ ] Registro completo en <60s desde Inicio.
- [ ] Resumen mensual cuadra: ingresos_mes − gastos_mes = balance_mes mostrado (RC-02). Saldo cuentas no cambia al filtrar por mes (RC-01).
- [ ] Presupuesto refleja gasto al crear movimiento (sin refresh manual). Restante negativo y % >100 se muestran correctamente (RC-03).
- [ ] Meta muestra faltante MAX(...,0) y ahorro/mes con meses inclusivos correctos tras aporte; sobrecumplida muestra excedente y requerido 0 (RC-04/RC-05).
- [ ] Aporte a meta NO modifica saldo de cuentas ni resumen (RN-09, Opción A) — verificado con test.
- [ ] Export JSON restaura 100% movimientos en cuenta limpia.
- [ ] Lighthouse PWA ≥90, instalable en Android/Chrome desktop.
- [ ] Usuario nuevo entiende “disponible, gastado, por ahorrar” sin ayuda (test 5s).

## 9. Métricas (§19) a instrumentar desde MVP

Eventos: `signup, primer_movimiento, movimientos_semana, crea_presupuesto/meta, consulta_resumen, tiempo_registro_ms, nps_claridad`. Tabla `events` mínima o PostHog stub.

## 10. Roadmap

Fase 0 Descubrimiento ✅ (documento concepto). Fase 1 MVP = este doc. Fase 2 Planificación (calendario, hábitos, recurrentes). Fase 3 Insights (simulador, pronóstico). Fase 4 Madurez (importación, recordatorios).

---
**Validar:** si marcas las 7 casillas §8 con datos reales de 1 mes, el MVP está listo para Fase 2.
