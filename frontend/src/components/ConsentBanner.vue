<template>
  <div v-if="visible" class="cookie-bar">
    <p><strong>Actualizamos nuestros documentos.</strong>
      <span class="sub">Para seguir usando CTD acepta los <a href="#" @click.prevent="$router.push('/terminos')">Términos</a>
      y la <a href="#" @click.prevent="$router.push('/datos')">Política de Datos</a>.</span></p>
    <label class="check"><input type="checkbox" v-model="t" /> Acepto los Términos y Condiciones</label>
    <label class="check"><input type="checkbox" v-model="d" /> Acepto la Política de Tratamiento de Datos</label>
    <button class="btn-mint" :disabled="!t || !d || busy" @click="aceptar">
      <span v-if="busy" class="spinner"></span>Aceptar y continuar
    </button>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../services/api'
import { useAuth } from '../stores/auth'
const auth = useAuth()
const visible = ref(false)
const t = ref(false); const d = ref(false); const busy = ref(false)
onMounted(async () => {
  if (!auth.isAuthed) return
  try {
    const { data } = await api.get('/auth/me')
    visible.value = !data.acepta_datos
  } catch { /* sin sesión válida: nada que pedir */ }
})
async function aceptar() {
  busy.value = true
  try {
    await api.post('/auth/consentimiento', { acepta_terminos: true, acepta_datos: true })
    visible.value = false
  } finally { busy.value = false }
}
</script>
<style>
.check{display:flex;gap:8px;align-items:flex-start;font-size:13px;color:var(--ink-soft)}.check input{margin-top:3px;accent-color:var(--mint-dark)}</style>
