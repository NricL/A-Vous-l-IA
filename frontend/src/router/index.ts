import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PrivacyView from '../views/PrivacyView.vue'
import FaqView from '../views/FaqView.vue'
import TermsView from '../views/TermsView.vue'
import { previewEnabled } from '../previewEnvironment'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...(import.meta.env.VITE_AVIA_PREVIEW === 'true' && previewEnabled(import.meta.env, window.location)
      ? [{ path: '/preview', name: 'preview', component: () => import('../views/PreviewView.vue') }]
      : []),
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/confidentialite',
      name: 'confidentialite',
      component: PrivacyView,
    },
    {
      path: '/faq',
      name: 'faq',
      component: FaqView,
    },
    {
      path: '/conditions-utilisation',
      name: 'conditions-utilisation',
      component: TermsView,
    },
  ],
})

if (import.meta.env.VITE_AVIA_PREVIEW === 'true') {
  router.beforeEach((to, from) => {
    // A document boundary prevents telemetry listeners from the normal app
    // surviving client-side navigation into the opt-in preview.
    if (from.matched.length && to.name !== from.name && (to.name === 'preview' || from.name === 'preview')) {
      window.location.assign(router.resolve(to).href)
      return false
    }
  })
}

export default router
