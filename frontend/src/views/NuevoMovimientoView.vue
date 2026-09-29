<template>
  <main class="page">
    <h2>Nuevo movimiento</h2>
    <form @submit.prevent="guardar" style="display: grid; gap: 12px">
      <select v-model="form.tipo" class="input"><option value="gasto">Gasto</option><option value="ingreso">Ingreso</option></select>
      <NumeroInput v-model="form.monto" placeholder="Monto (ej: 100.000)" required />
      <input v-model="form.descripcion" placeholder="Descripción" class="input" />
      <select v-model="form.cuenta_id" class="input" required>
        <option value="" disabled>Cuenta</option>
        <option v-for="c in cuentas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
      <select v-model="form.categoria_id" class="input" required>
        <option value="" disabled>Categoría</option>
        <option v-for="c in categoriasFiltradas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
      <select v-model="form.metodo_id" class="input">
        <option value="" disabled>Método (opcional)</option>
        <option v-for="m in metodos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
      </select>
      <input v-model="form.fecha" type="date" class="input" required />
      <button class="btn-primary" :disabled="loading || !valido">{{ loading ? 'Guardando…' : 'Guardar' }}</button>
      <p v-if="error" class="alert">{{ error }}</p>
    </form>
  </main>
</template>
<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import NumeroInput from '../components/NumeroInput.vue'
import api from '../services/api'
const router = useRouter()
const loading = ref(false)
const error = ref('')
const cuentas = ref<{ id: string; nombre: string }[]>([])
const categorias = ref<{ id: string; nombre: string; tipo: string }[]>([])
const metodos = ref<{ id: string; nombre: string }[]>([])
const form = reactive({ tipo: 'gasto', monto: null as number | null, descripcion: '', fecha: new Date().toISOString().slice(0, 10), cuenta_id: '', categoria_id: '', metodo_id: '' })

const categoriasFiltradas = computed(() =>
  categorias.value.filter((c) => c.tipo === form.tipo || c.tipo === 'ambos')
)
const valido = computed(() => form.monto && form.monto > 0 && form.fecha && form.cuenta_id && form.categoria_id)

onMounted(async () => {
  try {
    const [cu, ca, me] = await Promise.all([
      api.get('/cuentas'), api.get('/categorias', { params: { solo_activas: true } }), api.get('/metodos-pago')
    ])
    cuentas.value = cu.data
    categorias.value = ca.data
    metodos.value = me.data
    if (cuentas.value[0]) form.cuenta_id = cuentas.value[0].id
  } catch { error.value = 'No se pudieron cargar cuentas/categorías. Reintenta.' }
})

function detalle422(e: unknown): string {
  const r = (e as { response?: { data?: { detail?: unknown; field_errors?: Record<string, string> } } }).response?.data
  if (!r) return 'No se pudo guardar. Revisa monto, fecha y cuenta.'
  if (r.field_errors) return Object.entries(r.field_errors).map(([k, v]) => `${k}: ${v}`).join(' · ')
  if (Array.isArray(r.detail)) return r.detail.map((d: { loc?: string[]; msg?: string }) => `${d.loc?.slice(-1)}: ${d.msg}`).join(' · ')
  if (typeof r.detail === 'string') return r.detail
  return 'Datos inválidos (422). Revisa los campos.'
}

async function guardar() {
  loading.value = true; error.value = ''
  try {
    const payload = { ...form, categoria_id: form.categoria_id || null, metodo_id: form.metodo_id || null }
    await api.post('/movimientos', payload, { headers: { 'Idempotency-Key': crypto.randomUUID() } })
    router.push('/inicio')
  } catch (e: unknown) { error.value = detalle422(e) }
  finally { loading.value = false }
}
</script>
