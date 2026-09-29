import { defineStore } from 'pinia'
import api from '../services/api'

export const useResumen = defineStore('resumen', {
  state: () => ({ mes: new Date().toISOString().slice(0, 7), data: null as null | Record<string, number | string> }),
  actions: {
    async cargar() {
      const { data } = await api.get('/resumen', { params: { mes: this.mes } })
      this.data = data
    }
  }
})
