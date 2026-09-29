<template>
  <div ref="el" class="reveal"><slot /></div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { animacionesOff } from '../composables/usePerf'
const el = ref<HTMLElement | null>(null)
onMounted(() => {
  if (!el.value || animacionesOff()) {
    el.value?.classList.add('in')
    return
  }
  const io = new IntersectionObserver(
    ([e]) => {
      if (e.isIntersecting) {
        el.value?.classList.add('in')
        io.disconnect()
      }
    },
    { threshold: 0.12 }
  )
  io.observe(el.value)
})
</script>
<style>
.reveal { opacity: 0; transform: translateY(14px); transition: opacity 0.5s ease, transform 0.5s ease; }
.reveal.in { opacity: 1; transform: none; }
</style>
