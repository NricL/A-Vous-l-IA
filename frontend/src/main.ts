import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { initializeAppInsights } from './appinsights'

const app = createApp(App)

// Initialize Application Insights telemetry
const instrumentationKey = import.meta.env.VITE_APPINSIGHTS_KEY || ''
if (instrumentationKey) {
  const appInsights = initializeAppInsights(instrumentationKey)
  
  // Track chat session start on load
  if (!document.body.getAttribute('data-case-hash')) {
    appInsights.trackChatSessionStart()
  } else {
    // Parcours page: track page opened
    appInsights.trackParcoursPageOpened()
  }
  
  // Make available globally for components
  app.config.globalProperties.$appInsights = appInsights
} else {
  console.warn('[Telemetry] VITE_APPINSIGHTS_KEY not set - telemetry disabled')
}

app.use(createPinia())
app.use(router)

app.mount('#app')
