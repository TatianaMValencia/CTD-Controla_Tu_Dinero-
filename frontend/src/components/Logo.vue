<template>
  <img :key="tema" :src="tema === 'dark' ? logoDark : logo" alt="CTD" :width="width" />
</template>
<script setup lang="ts">
import logo from '../assets/logo.png'
import logoDark from '../assets/logo-dark.png'
import { useTema } from '../composables/useTema'
defineProps<{ width?: number }>()
const { tema } = useTema()
</script>
