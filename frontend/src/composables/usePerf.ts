/** Rendimiento adaptativo: aparatos débiles o con ahorro de datos ven todo estático. */
export function initPerf() {
  const params = new URLSearchParams(location.search)
  const nav = navigator as Navigator & { deviceMemory?: number; connection?: { saveData?: boolean } }
  const forced = params.get('perf')
  const lite =
    forced === 'lite' ||
    (forced !== 'full' &&
      (matchMedia('(prefers-reduced-motion: reduce)').matches ||
        (navigator.hardwareConcurrency || 8) <= 4 ||
        (nav.deviceMemory || 8) < 4 ||
        !!nav.connection?.saveData))
  document.documentElement.dataset.perf = lite ? 'lite' : 'full'
}

export function animacionesOff(): boolean {
  if (new URLSearchParams(location.search).get('perf') === 'full') return false
  return (
    document.documentElement.dataset.perf === 'lite' ||
    matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}
