import { ref } from 'vue'

/** Tema global CTD: persiste en localStorage y se aplica al <html>. */
const tema = ref(localStorage.getItem('ctd-theme') || 'light')

function faviconPorTema(t: string) {
  const link = document.querySelector<HTMLLinkElement>("link[rel='icon']")
  if (link) link.href = t === 'dark' ? '/icons/favicon-dark.ico' : '/icons/favicon.ico'
}

export function useTema() {
  function aplicar(t: string) {
    tema.value = t
    localStorage.setItem('ctd-theme', t)
    document.documentElement.dataset.theme = t
    faviconPorTema(t)
  }
  function init() {
    document.documentElement.dataset.theme = tema.value
    faviconPorTema(tema.value)
  }
  return { tema, aplicar, init }
}
