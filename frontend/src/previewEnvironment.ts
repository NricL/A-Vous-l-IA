export interface PreviewEnvironment {
  BASE_URL?: string
  VITE_AVIA_PREVIEW?: string
  VITE_AVIA_PREVIEW_CLOUD?: string
  VITE_AVIA_PREVIEW_ORIGIN?: string
  VITE_AVIA_PREVIEW_HOSTS?: string
}

const loopback = ['localhost', '127.0.0.1', '[::1]']

function httpsOrigin(value: string): string {
  const url = new URL(value)
  if (url.protocol !== 'https:' || url.username || url.password
    || (value !== url.origin && value !== `${url.origin}/`)) {
    throw new Error('Une origine HTTPS exacte est requise, sans chemin, identifiants ni paramètres.')
  }
  return url.origin
}

export function previewOrigin(configured: string, approvedCloudOrigin = ''): string {
  if (approvedCloudOrigin) {
    const approved = httpsOrigin(approvedCloudOrigin)
    if (httpsOrigin(configured) !== approved) throw new Error('Origine de test non autorisée.')
    return approved
  }
  const url = new URL(configured)
  const port = Number(url.port)
  if (url.protocol !== 'http:' || !loopback.includes(url.hostname) || url.username || url.password
    || (configured !== url.origin && configured !== `${url.origin}/`)
    || !Number.isInteger(port) || port < 1024 || port > 65535) {
    throw new Error('La préversion locale exige une origine HTTP de bouclage avec un port explicite.')
  }
  return url.origin
}

export function previewEnabled(env: PreviewEnvironment, location: Pick<Location, 'origin' | 'hostname'>): boolean {
  if (env.VITE_AVIA_PREVIEW !== 'true') return false
  if (env.VITE_AVIA_PREVIEW_CLOUD !== 'true') return loopback.includes(location.hostname)
  try {
    httpsOrigin(env.VITE_AVIA_PREVIEW_ORIGIN ?? '')
    const hosts = (env.VITE_AVIA_PREVIEW_HOSTS ?? '').split(',').map(value => httpsOrigin(value.trim()))
    return hosts.includes(location.origin)
  } catch {
    return false
  }
}

// Vue Router's default matching is case-insensitive and accepts one trailing slash.
export function previewPath(pathname: string, base = '/'): boolean {
  const prefix = base.replace(/\/$/, '')
  if (prefix && pathname.slice(0, prefix.length).toLowerCase() !== prefix.toLowerCase()) return false
  return /^\/preview\/?$/i.test(pathname.slice(prefix.length))
}

export function isPreviewLocation(
  env: PreviewEnvironment, location: Pick<Location, 'origin' | 'hostname' | 'pathname'>,
): boolean {
  return previewEnabled(env, location) && previewPath(location.pathname, env.BASE_URL)
}
