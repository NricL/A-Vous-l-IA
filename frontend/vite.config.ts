import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const previewEnabled = loadEnv(mode, process.cwd()).VITE_AVIA_PREVIEW === 'true'
  return {
  base: "/",
  plugins: [
    vue(),
    ...(!previewEnabled ? [vueDevTools()] : []),
    ...(previewEnabled ? [{
      name: 'isolated-preview-html',
      transformIndexHtml: {
        order: 'pre' as const,
        handler(html: string) {
          // Keep the normal app's font links, but never contact a font host on preview.
          const fontLinks = html.match(/<link\b[^>]*https:\/\/fonts\.(?:googleapis|gstatic)\.com[^>]*>/g) ?? []
          return html.replace(/<link\b[^>]*https:\/\/fonts\.(?:googleapis|gstatic)\.com[^>]*>/g, '')
            .replace('</head>', `<script type="module">
              import { isPreviewLocation } from '/src/previewEnvironment.ts'
              if (isPreviewLocation(import.meta.env, window.location)) {
                const meta = document.createElement('meta')
                meta.name = 'referrer'
                meta.content = 'no-referrer'
                document.head.append(meta)
              } else {
                document.head.insertAdjacentHTML('beforeend', ${JSON.stringify(fontLinks.join(''))})
              }
            </script></head>`)
        },
      },
    }] : []),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  }
})
