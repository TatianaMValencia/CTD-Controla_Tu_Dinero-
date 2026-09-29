<template>
  <main class="page">
    <div class="eyebrow">DATOS</div>
    <p>Lo que está pasando con tu dinero.</p>
    <div class="eyebrow">BALANCE DE {{ mesLabel }}</div>
    <div class="big-number" :style="{ color: balance >= 0 ? '#00B37A' : 'var(--danger)' }">{{ balance >= 0 ? '+' : '−' }}${{ fmt(Math.abs(balance)) }}</div>
    <div class="grid-2" style="margin-top: 8px">
      <div>Ingresaste<div><strong>${{ fmt(ingresos) }}</strong></div></div>
      <div>Gastaste<div><strong>${{ fmt(gastos) }}</strong></div></div>
    </div>
    <hr class="divider" />
    <div class="eyebrow">DISTRIBUCIÓN DE GASTOS</div>
    <svg viewBox="0 0 120 120" width="140" style="margin: 8px auto; display: block" v-if="dist.length">
      <circle cx="60" cy="60" r="44" fill="none" stroke="var(--line)" stroke-width="16" />
      <circle v-for="(s, i) in segmentos" :key="i" cx="60" cy="60" r="44" fill="none"
        :stroke="s.color" stroke-width="16" stroke-linecap="round"
        :stroke-dasharray="`${s.len} ${CIRC - s.len}`" :stroke-dashoffset="-s.off"
        transform="rotate(-90 60 60)" />
    </svg>
    <div v-for="d in dist" :key="d.nombre" class="row"><span>{{ d.nombre }}</span><strong>{{ d.porcentaje }}%</strong></div>
    <p class="sub">{{ fraseDist }}</p>
    <hr class="divider" />
    <div class="eyebrow">EVOLUCIÓN (ÚLTIMOS {{ evo.length }} MESES)</div>
    <svg viewBox="0 0 200 80" width="100%" v-if="evo.length">
      <rect v-for="(b, i) in barras" :key="b.mes" :x="10 + i * 30" :y="76 - b.h" width="16" :height="b.h" rx="4"
        :fill="i === barras.length - 1 ? '#00FFAB' : '#050B3B'">
        <title>{{ b.mes }}: ${{ fmt(b.balance_mes) }}</title>
      </rect>
      <text v-for="(b, i) in barras" :key="'t' + b.mes" :x="18 + i * 30" y="79" font-size="7" text-anchor="middle" fill="var(--ink-soft)">{{ b.mes.slice(5) }}</text>
    </svg>
    <p class="sub">{{ mensajeEvo }}</p>
  </main>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../services/api'
const mes = ref(new Date().toISOString().slice(0, 7))
const ingresos = ref(0); const gastos = ref(0); const balance = ref(0)
const dist = ref<{ nombre: string; porcentaje: number }[]>([])
const evo = ref<{ mes: string; ingresos: number; gastos: number; balance_mes: number }[]>([])
const mensajeEvo = ref('')
const fmt = (n: number) => Number(n ?? 0).toLocaleString('es-CO')
const mesLabel = computed(() => {
  const [y, m] = mes.value.split('-').map(Number)
  const n = new Date(y, m - 1).toLocaleDateString('es-CO', { month: 'long', year: 'numeric' })
  return n.toUpperCase()
})
const fraseDist = computed(() => dist.value[0] ? `Tu mayor categoría de gasto fue ${dist.value[0].nombre}.` : 'Sin gastos en el periodo.')
// Dona sincronizada con los % reales
const CIRC = 2 * Math.PI * 44
const PALETA = ['#16B98B', '#5CF2C0', '#050B3B', '#8CA0B8', '#E2E8F0', '#D89A27']
const segmentos = computed(() => {
  let acc = 0
  return dist.value.map((d, i) => {
    const len = Math.max((d.porcentaje / 100) * CIRC - (dist.value.length > 1 ? 2 : 0), 0)
    const s = { len, off: acc, color: PALETA[i % PALETA.length] }
    acc += (d.porcentaje / 100) * CIRC
    return s
  })
})
const barras = computed(() => {
  const max = Math.max(...evo.value.map((b) => Math.abs(b.balance_mes)), 0) || 1
  return evo.value.map((b) => ({ ...b, h: Math.max(Math.round((Math.abs(b.balance_mes) / max) * 64), 3) }))
})
onMounted(async () => {
  const r = await api.get('/resumen', { params: { mes: mes.value } }).catch(() => null)
  if (r) { ingresos.value = r.data.ingresos; gastos.value = r.data.gastos; balance.value = r.data.balance_mes }
  const d = await api.get('/reportes/distribucion', { params: { tipo: 'gasto' } }).catch(() => null)
  if (d) dist.value = d.data.slice(0, 6)
  const e = await api.get('/reportes/evolucion', { params: { meses: 6 } }).catch(() => null)
  if (e) { evo.value = e.data.items ?? []; mensajeEvo.value = e.data.mensaje ?? '' }
})
</script>
<style>.row{display:flex;justify-content:space-between;padding:8px 2px;border-bottom:1px solid var(--line)}.sub{font-size:13px;opacity:.65}</style>
