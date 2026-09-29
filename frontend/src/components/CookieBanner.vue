<template>
  <div v-if="visible" class="cookie-bar">
    <p><strong>Cookies necesarias.</strong> <span class="sub">Guardamos tu sesión y preferencias en este dispositivo. Sin rastreadores.</span>
      <a href="#" @click.prevent="$router.push('/cookies')">Ver política</a></p>
    <div class="row2">
      <button class="btn-mint" @click="elegir('all')">Aceptar</button>
      <button class="btn-ghost" @click="elegir('min')">Solo necesarias</button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const visible = ref(!localStorage.getItem('ctd-cookies'))
function elegir(v: string) {
  localStorage.setItem('ctd-cookies', v)
  visible.value = false
}
</script>
<style>
.cookie-bar {
  position: fixed; left: 12px; right: 12px; bottom: 12px; z-index: 40;
  background: var(--surface); color: var(--ink);
  border: 1px solid var(--line); border-radius: 16px;
  padding: 14px; box-shadow: var(--shadow);
  display: grid; gap: 10px;
  animation: rise 240ms ease-out;
}
.cookie-bar p { margin: 0; font-size: 14px; }
.cookie-bar .row2 { display: flex; gap: 8px; }
</style>
