import { ref } from 'vue'
import { registerSW } from 'virtual:pwa-register'

/** Detector de actualizaciones: avisa y aplica sin reinstalar. */
const hayUpdate = ref(false)
const buscando = ref(false)
let ctrl: ((reload: boolean) => Promise<void>) | null = null

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  ctrl = registerSW({
    immediate: true,
    onNeedRefresh() {
      hayUpdate.value = true
    },
    onRegisteredSW(swUrl, r) {
      // Revisa cada 30 min y al volver a la app
      if (r) {
        setInterval(() => r.update().catch(() => {}), 30 * 60 * 1000)
        document.addEventListener('visibilitychange', () => {
          if (!document.hidden) r.update().catch(() => {})
        })
      }
      void swUrl
    }
  })
}

export function usePwaUpdate() {
  async function buscar() {
    buscando.value = true
    try {
      const reg = await navigator.serviceWorker?.getRegistration()
      await reg?.update()
      // Si no apareció nada en 4s, está al día
      setTimeout(() => {
        if (!hayUpdate.value) buscando.value = false
      }, 4000)
    } catch {
      buscando.value = false
    }
  }
  async function aplicar() {
    await ctrl?.(true)
  }
  return { hayUpdate, buscando, buscar, aplicar }
}
