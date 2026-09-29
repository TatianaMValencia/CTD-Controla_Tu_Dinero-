import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import { initPerf } from './composables/usePerf'
import router from './router'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './styles/tokens.css'

initPerf()
createApp(App).use(createPinia()).use(router).mount('#app')
