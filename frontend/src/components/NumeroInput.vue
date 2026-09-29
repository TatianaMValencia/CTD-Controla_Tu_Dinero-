<template>
  <input
    ref="inputEl"
    :value="texto"
    @input="onInput"
    @blur="onBlur"
    :inputmode="modo === 'telefono' ? 'tel' : 'decimal'"
    :placeholder="placeholder"
    :required="required"
    class="input"
    :style="{ textAlign: modo === 'dinero' ? 'right' : undefined, fontVariantNumeric: 'tabular-nums' }"
  />
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{ modelValue: number | string | null | undefined; modo?: 'dinero' | 'telefono'; placeholder?: string; required?: boolean }>(),
  { modo: 'dinero', placeholder: '', required: false }
)
const emit = defineEmits<{ (e: 'update:modelValue', v: number | string | null): void }>()

const texto = ref('')
const inputEl = ref<HTMLInputElement | null>(null)

function grupos(n: string): string {
  return n.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

function formatearDinero(raw: string): { texto: string; valor: number | null } {
  const limpio = raw.replace(/[^0-9.,]/g, '')
  if (!limpio) return { texto: '', valor: null }
  const m = limpio.match(/^(.*?)[.,](\d{1,2})$/)
  let ent: string, dec = ''
  if (m) {
    ent = m[1].replace(/[^0-9]/g, '')
    dec = m[2]
  } else {
    ent = limpio.replace(/[^0-9]/g, '')
  }
  ent = ent.replace(/^0+(?=\d)/, '')
  const t = grupos(ent || '0') + (dec ? `,${dec}` : '')
  const v = Number(`${ent || '0'}${dec ? `.${dec}` : ''}`)
  return { texto: t, valor: Number.isFinite(v) ? v : null }
}

function formatearTelefono(raw: string): { texto: string; valor: string | null } {
  const d = raw.replace(/\D/g, '').slice(0, 12)
  if (!d) return { texto: '', valor: null }
  const p = [d.slice(0, 3), d.slice(3, 6), d.slice(6, 10), d.slice(10)].filter(Boolean)
  return { texto: p.join(' '), valor: d }
}

function aplicar(v: number | string | null | undefined) {
  if (props.modo === 'telefono') {
    const r = formatearTelefono(String(v ?? ''))
    texto.value = r.texto
    return r.valor
  }
  if (typeof v === 'number') {
    const [e, d] = String(v).split('.')
    texto.value = grupos(e) + (d ? `,${d.slice(0, 2)}` : '')
    return v
  }
  const r = formatearDinero(String(v ?? ''))
  texto.value = r.texto
  return r.valor
}

function onInput(e: Event) {
  const v = (e.target as HTMLInputElement).value
  const r = props.modo === 'telefono' ? formatearTelefono(v) : formatearDinero(v)
  texto.value = r.texto
  // Repone el cursor al final (los separadores cambian la longitud)
  requestAnimationFrame(() => {
    const el = e.target as HTMLInputElement
    el.setSelectionRange(el.value.length, el.value.length)
  })
  emit('update:modelValue', r.valor)
}

function onBlur() {
  // Al salir, re-formatea el valor canónico
  emit('update:modelValue', aplicar(props.modelValue))
}

watch(
  () => props.modelValue,
  (v) => {
    // No pisar lo que el usuario está escribiendo; solo al entrar o al salir
    if (document.activeElement === inputEl.value) return
    aplicar(v)
  },
  { immediate: true }
)
</script>
