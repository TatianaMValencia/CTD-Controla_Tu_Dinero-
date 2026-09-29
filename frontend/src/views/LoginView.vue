<template>
  <div class="auth-wrap">
    <main class="page rise" style="max-width: 400px">
      <div style="display: flex; justify-content: flex-end">
        <button type="button" class="theme-toggle" @click="toggleTema" :aria-label="oscuro ? 'Modo claro' : 'Modo oscuro'">
          <i :class="['bi', oscuro ? 'bi-sun' : 'bi-moon']"></i>
        </button>
      </div>
      <div style="text-align: center; margin: 8px 0 8px">
        <Logo :width="72" />
        <h2 style="margin: 12px 0 4px">Bienvenido a CTD</h2>
        <p class="sub">Controla tu dinero con mayor claridad.</p>
      </div>
      <form @submit.prevent="login" style="display: grid; gap: 12px">
        <div class="field">
          <label for="correo">Correo electrónico</label>
          <input id="correo" v-model="correo" type="email" placeholder="tucorreo@gmail.com" class="input" required />
        </div>
        <div class="field">
          <label for="pass">Contraseña</label>
          <div class="pass-wrap">
            <input id="pass" v-model="password" :type="ver ? 'text' : 'password'" placeholder="••••••••" class="input" required />
            <button type="button" class="pass-eye" @click="ver = !ver" aria-label="Mostrar contraseña"><i :class="['bi', ver ? 'bi-eye-slash' : 'bi-eye']"></i></button>
          </div>
        </div>
        <button class="btn-primary" :disabled="loading">{{ loading ? 'Entrando…' : 'Entrar' }}</button>
        <p v-if="error" class="alert">{{ error }}</p>
      </form>
      <p class="sub" style="text-align: center; margin-top: 16px">¿Sin cuenta? <a href="#" @click.prevent="$router.push('/registro')">Crear cuenta</a></p>
    </main>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import Logo from '../components/Logo.vue'
import { useTema } from '../composables/useTema'
import api from '../services/api'
import { useAuth } from '../stores/auth'
const router = useRouter()
const auth = useAuth()
const { tema, aplicar } = useTema()
const oscuro = computed(() => tema.value === 'dark')
function toggleTema() { aplicar(oscuro.value ? 'light' : 'dark') }
const correo = ref(''); const password = ref(''); const error = ref('')
const ver = ref(false); const loading = ref(false)
async function login() {
  error.value = ''; loading.value = true
  const email = correo.value.trim().toLowerCase()
  try {
    const { data } = await api.post('/auth/login', { correo: email, password: password.value })
    if (data.requires_2fa) {
      localStorage.setItem('pending_2fa_email', email)
      router.push({ path: '/2fa', query: { correo: email } })
      return
    }
    auth.setTokens(data.access_token, data.refresh_token)
    await auth.entrar(router)
  } catch (err: unknown) {
    const r = (err as { response?: { status?: number; data?: { detail?: string } } }).response
    error.value = r?.status === 422 ? 'Revisa el correo: sin espacios ni mayúsculas.' : (r?.data?.detail ?? 'Credenciales inválidas')
  } finally { loading.value = false }
}
</script>
<style>.link{background:none;border:0;color:var(--ink-soft)}</style>
