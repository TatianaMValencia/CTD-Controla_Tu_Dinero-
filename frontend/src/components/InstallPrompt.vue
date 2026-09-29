<template>
  <div v-if="visible" class="install-bar">
    <Logo :width="36" />
    <div style="flex: 1"><strong>Instala CTD</strong><small>Acceso rápido y funciona sin conexión.</small></div>
    <button class="btn-mint" @click="instalar">Instalar</button>
    <button class="btn-ghost" style="color: #fff; border-color: rgba(255,255,255,.3)" @click="cerrar">No</button>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Logo from './Logo.vue'
const visible = ref(false)
let deferred: { prompt: () => void } | null = null
onMounted(() => {
  if (localStorage.getItem('ctd-install-no')) return
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferred = e as unknown as { prompt: () => void }
    visible.value = true
  })
})
async function instalar() { visible.value = false; deferred?.prompt(); deferred = null }
function cerrar() { visible.value = false; localStorage.setItem('ctd-install-no', '1') }
</script>
