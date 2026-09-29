import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../services/api'

/** Sesión reactiva: App.vue y vistas reaccionan a login/logout sin recargar. */
export const useAuth = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access_token'))
  const refresh = ref(localStorage.getItem('refresh_token'))
  const onboardingDone = ref(localStorage.getItem('ctd-onboarding') === '1')

  const isAuthed = computed(() => !!access.value)

  function setTokens(a: string, r: string) {
    access.value = a
    refresh.value = r
    localStorage.setItem('access_token', a)
    localStorage.setItem('refresh_token', r)
  }

  function setOnboarding(done: boolean) {
    onboardingDone.value = done
    if (done) localStorage.setItem('ctd-onboarding', '1')
    else localStorage.removeItem('ctd-onboarding')
  }

  function clear() {
    access.value = null
    refresh.value = null
    onboardingDone.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('pending_2fa_email')
    localStorage.removeItem('ctd-onboarding')
  }

  async function logout() {
    try { await api.post('/auth/logout') } catch { /* stateless: igual se sale */ }
    clear()
  }

  /** Tras login: trae /auth/me y decide onboarding vs inicio. */
  async function entrar(router: { push: (p: string) => void }) {
    try {
      const { data } = await api.get('/auth/me')
      setOnboarding(!!data.onboarding_done)
      router.push(data.onboarding_done ? '/inicio' : '/onboarding')
    } catch {
      router.push('/inicio')
    }
  }

  return { access, refresh, onboardingDone, isAuthed, setTokens, setOnboarding, clear, logout, entrar }
})
