import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import ts from 'typescript'
import * as vue from 'vue'
import { parse } from 'vue/compiler-sfc'
import { createRouter, createMemoryHistory } from 'vue-router'
import { renderToString } from '@vue/server-renderer'

const environmentSource = readFileSync(new URL('../src/previewEnvironment.ts', import.meta.url), 'utf8')
const environmentExports = {}
new Function('exports', ts.transpile(environmentSource, {
  target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS,
}))(environmentExports)
const apiSource = readFileSync(new URL('../src/api/preview.ts', import.meta.url), 'utf8')
function loadApi(env = {}, fetch = globalThis.fetch) {
  const exports = {}
  const apiCode = ts.transpile(apiSource.replaceAll('import.meta.env', 'env'), { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS })
  new Function('exports', 'require', 'env', 'fetch', apiCode)(exports, () => environmentExports, env, fetch)
  return exports
}
const apiExports = loadApi()
const backend = 'https://avoulia-backend--qual-20260913-r1.purpleocean-980317d1.francecentral.azurecontainerapps.io'
const azure = 'https://avoulia-frontend--qual-20260913-r1.purpleocean-980317d1.francecentral.azurecontainerapps.io'
const pages = 'https://nricl.github.io'
const cloudEnv = {
  VITE_AVIA_PREVIEW: 'true', VITE_AVIA_PREVIEW_CLOUD: 'true',
  VITE_AVIA_PREVIEW_ORIGIN: backend, VITE_AVIA_PREVIEW_HOSTS: `${azure},${pages}`,
}

test('local and approved cloud preview aliases never initialize telemetry before consent', () => {
  const source = readFileSync(new URL('../src/main.ts', import.meta.url), 'utf8')
    .replace(/^import .*$/gm, '')
    .replaceAll('import.meta.env', 'env')
  const compiled = ts.transpile(source, { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.None })
  const initialize = new Function('env', 'window', 'document', 'console', 'createApp', 'createPinia',
    'App', 'router', 'initializeAppInsights', 'isPreviewLocation', compiled)
  for (const [origin, base, config, approved] of [
    ['http://127.0.0.1:5173', '/', {}, true],
    [azure, '/', cloudEnv, true],
    [pages, '/A-Vous-l-IA/', cloudEnv, true],
    ['https://unapproved.example', '/', cloudEnv, false],
  ]) {
   for (const path of ['preview', 'preview/', 'PREVIEW', 'Preview/', '', 'faq', 'preview//', 'preview-extra']) {
    for (const enabled of [true, false]) {
      let starts = 0
      const app = { use() {}, mount() {}, config: { globalProperties: {} } }
      initialize(
        { ...config, BASE_URL: base, VITE_AVIA_PREVIEW: String(enabled), VITE_APPINSIGHTS_KEY: 'synthetic-key' },
        { location: new URL(`${base}${path}`, origin) },
        { body: { getAttribute() { return null } } }, { info() {}, warn() {} },
        () => app, () => ({}), {}, {},
        () => { starts++; return { trackChatSessionStart() {}, trackParcoursPageOpened() {} } },
        environmentExports.isPreviewLocation,
      )
      const preview = /^preview\/?$/i.test(path)
      assert.equal(starts, enabled && approved && preview ? 0 : 1, `${origin}${base}${path} preview=${enabled}`)
    }
   }
  }
})

const routerSource = readFileSync(new URL('../src/router/index.ts', import.meta.url), 'utf8')
  .replace(/^import .*$/gm, '').replaceAll('import.meta.env', 'env').replace('export default router', 'return router')
const loadRouter = new Function('env', 'window', 'createRouter', 'createWebHistory', 'previewEnabled',
  'HomeView', 'PrivacyView', 'FaqView', 'TermsView',
  ts.transpile(routerSource, { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.None }))
function actualRouter(env, location) {
  return loadRouter(env, { location }, createRouter, createMemoryHistory, environmentExports.previewEnabled, {}, {}, {}, {})
}

test('real Vue Router resolves the same preview aliases as telemetry, including Pages base', () => {
  for (const [origin, base, config] of [
    ['http://localhost:5173', '/', { VITE_AVIA_PREVIEW: 'true' }],
    [azure, '/', cloudEnv], [pages, '/A-Vous-l-IA/', cloudEnv],
  ]) {
    const env = { ...config, BASE_URL: base }
    const router = actualRouter(env, new URL(origin))
    for (const alias of ['/preview', '/preview/', '/PREVIEW', '/Preview/']) {
      const route = router.resolve(alias)
      assert.equal(route.name, 'preview')
      assert.equal(route.href, `${base.slice(0, -1)}${alias}`)
      assert.equal(environmentExports.isPreviewLocation(env, new URL(route.href, origin)), true)
    }
    assert.equal(router.resolve('/').name, 'home')
    assert.equal(environmentExports.isPreviewLocation(env, new URL(base, origin)), false)
    for (const path of ['/preview//', '/preview/x', '/previewish', '/other/preview', '/A-Vous-l-IA-extra/preview']) {
      assert.equal(environmentExports.previewPath(path, base), false)
    }
  }
})

test('preview route is absent for disabled flag, missing config or unapproved origin', () => {
  for (const env of [
    { ...cloudEnv, VITE_AVIA_PREVIEW: 'false' },
    { ...cloudEnv, VITE_AVIA_PREVIEW_HOSTS: '*' },
    { ...cloudEnv, VITE_AVIA_PREVIEW_ORIGIN: '' },
    { ...cloudEnv, VITE_AVIA_PREVIEW_HOSTS: `${azure}/path` },
    { ...cloudEnv, VITE_AVIA_PREVIEW_HOSTS: '' },
    { VITE_AVIA_PREVIEW: 'true' },
  ]) {
    const router = actualRouter(env, new URL(azure))
    assert.equal(router.hasRoute('preview'), false)
    assert.equal(router.resolve('/').name, 'home')
  }
  for (const origin of ['http://nricl.github.io', 'https://nricl.github.io.evil.example', 'https://elsewhere.example', `${azure}:8443`]) {
    assert.equal(actualRouter(cloudEnv, new URL(origin)).hasRoute('preview'), false)
  }
})

test('crossing the preview boundary reloads the document instead of retaining telemetry listeners', async () => {
  const assigned = []
  const location = { origin: pages, hostname: 'nricl.github.io', assign: href => assigned.push(href) }
  const env = { ...cloudEnv, BASE_URL: '/A-Vous-l-IA/' }
  const router = actualRouter(env, location)
  await router.push('/')
  await router.push('/PREVIEW/')
  assert.deepEqual(assigned, ['/A-Vous-l-IA/preview'])
  assert.equal(router.currentRoute.value.name, 'home')
  const fromPreview = actualRouter(env, location)
  // Replace only the lazy SFC loader: exercise the production navigation guard.
  fromPreview.addRoute({ path: '/preview', name: 'preview', component: {} })
  await fromPreview.push('/preview')
  await fromPreview.push('/')
  assert.equal(assigned.at(-1), '/A-Vous-l-IA/')
  assert.equal(fromPreview.currentRoute.value.name, 'preview')
})

test('exact HTTPS API origin is allowed only by explicit cloud build configuration', () => {
  assert.equal(environmentExports.previewOrigin(backend, backend), backend)
  assert.equal(loadApi(cloudEnv).PREVIEW_ORIGIN, backend)
  assert.throws(() => environmentExports.previewOrigin(backend))
  for (const origin of [
    'https://unapproved.example', backend.replace('https:', 'http:'), `${backend}/path`,
    `${backend}/.`, `${backend}/?`, `${backend}#`, `${backend}?q=x`, `${backend}:8443`,
    backend.replace('https://', 'https://user:pass@'), `${backend}.evil.example`, '*',
  ]) assert.throws(() => environmentExports.previewOrigin(origin, backend), origin)
})

const sample = (revision = 0, session = 'session-a') => ({
  protocol_version: 1, session_id: session, revision, catalogue_revision: 'source-a',
  phase: 'domain', question: { id: `question-${revision}`, options: [], prompt: 'Question arbitraire' },
  initial_need: '', problem_original: '', confirmed: {}, diagnostics: {},
  allowed_actions: [], back_targets: [], card: null, warning: '',
})

test('canonical command envelope is independent of all display text', () => {
  const state = sample()
  const action = { action: 'choose', choice_id: 'objective:canonical-source-id' }
  const before = apiExports.actionEnvelope(state, action, 'request-a')
  state.question.prompt = 'Une autre formulation'
  state.question.options = [{ id: action.choice_id, label: 'Libellé affiché modifié' }]
  assert.deepEqual(apiExports.actionEnvelope(state, action, 'request-a'), before)
  assert.equal(before.question_id, 'question-0')
  assert.equal(before.choice_id, 'objective:canonical-source-id')
})

test('response guard refuses older revisions, another session and another protocol', () => {
  assert.equal(apiExports.acceptsResponse(sample(3), sample(2), 'session-a'), false)
  assert.equal(apiExports.acceptsResponse(sample(3), sample(4, 'other'), 'session-a'), false)
  assert.equal(apiExports.acceptsResponse(sample(3), { ...sample(4), protocol_version: 2 }, 'session-a'), false)
  assert.equal(apiExports.acceptsResponse(sample(3), sample(4), 'session-a'), true)
  assert.equal(apiExports.acceptsResponse(sample(3), sample(3), 'session-a'), true)
})

const component = readFileSync(new URL('../src/views/PreviewView.vue', import.meta.url), 'utf8')
const setup = parse(component).descriptor.scriptSetup.content
  .replace(/import \{[\s\S]*?\} from 'vue'/, '')
  .replace(/import \{[\s\S]*?\} from '@\/api\/preview'/, '')
  .replaceAll('import.meta.env', 'env')
const setupJS = ts.transpile(setup, { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.None })
const createSetup = new Function('dependencies', `
  const { ref, computed, onMounted, onBeforeUnmount, createPreview, readPreview,
    sendPreviewAction, acceptsResponse, PREVIEW_ORIGIN, readPreviewSource, CLOUD_PREVIEW, env } = dependencies;
  ${setupJS}
  return { state, busy, error, initialNeed, problem, choiceText, start, submit, refresh, choose, chooseText, parcoursUrl,
    initialize, source, externalConsent, publicMode, pagesMode, selectedMode, changeSource,
    CLOUD_PREVIEW, homeUrl, PREVIEW_ORIGIN, phase, labels, prompt, currentSource, selections, externalMode, diagnostics };
`)

function fixture(t, overrides = {}) {
  const requests = []
  const pending = []
  let createCount = 0
  const scope = vue.effectScope()
  t.after(() => scope.stop())
  const instance = scope.run(() => createSetup({
    ...vue, onMounted: () => {}, onBeforeUnmount: () => {}, CLOUD_PREVIEW: false, env: { BASE_URL: '/' },
    PREVIEW_ORIGIN: 'http://127.0.0.1:8767',
    acceptsResponse: apiExports.acceptsResponse,
    createPreview: async () => sample(0, `session-${++createCount}`),
    readPreviewSource: async () => ({ source_mode: 'SYNTHETIC' }),
    readPreview: async () => instance.state.value,
    sendPreviewAction: (state, action, requestId) => {
      requests.push({ state, action, requestId })
      return new Promise(resolve => pending.push(resolve))
    },
    ...overrides,
  }))
  instance.state.value = sample()
  instance.source.value = { source_mode: 'SYNTHETIC', case_count: 16 }
  return { instance, requests, pending }
}

test('real component suppresses duplicate clicks and sends canonical identities', async t => {
  const f = fixture(t)
  const first = f.instance.choose('marketing_visibilite')
  await f.instance.choose('production')
  assert.equal(f.requests.length, 1)
  assert.equal(f.requests[0].action.choice_id, 'marketing_visibilite')
  f.pending[0]({ ...sample(1), phase: 'sector' })
  await first
  assert.equal(f.instance.state.value.phase, 'sector')
  assert.equal(f.instance.busy.value, false)
})

test('old response cannot overwrite a newly started session', async t => {
  const f = fixture(t)
  const first = f.instance.choose('marketing_visibilite')
  await f.instance.start()
  const newSession = f.instance.state.value.session_id
  f.pending[0]({ ...sample(1), phase: 'sector' })
  await first
  assert.equal(f.instance.state.value.session_id, newSession)
  assert.equal(f.instance.state.value.phase, 'domain')
})

test('initial problem including negatives is sent untouched', async t => {
  const f = fixture(t)
  const need = "améliorer la pertinence des description produit pour l'adapter à la GenZ, sans WhatsApp"
  f.instance.initialNeed.value = need
  const first = f.instance.choose('marketing_visibilite')
  assert.equal(f.requests[0].action.initial_need, need)
  f.pending[0]({ ...sample(1), phase: 'sector', initial_need: need, problem_original: need })
  await first
  assert.equal(f.instance.problem.value, need)
})

test('UI has immediate domain question, loud fixture provenance, diagnosis and terminal-only card', () => {
  assert.match(component, /Dans quel domaine souhaitez-vous avancer/)
  assert.match(component, /SYNTHÉTIQUE · NON PRODUCTION/)
  assert.match(component, /Diagnostic de test/)
  assert.match(component, /phase === 'problem'/)
  assert.match(component, /cas fictifs, pas le RAG réel/)
  assert.match(component, /Ouvrir le parcours de test/)
  assert.equal((component.match(/class="primary link"/g) || []).length, 1)
  assert.doesNotMatch(component, /detectPhase|detect_expected|localStorage|sessionStorage|trackEvent|v-html|catch\s*\{/)
})

test('typed option is sent verbatim with current question, cleared after transition', async t => {
  const f = fixture(t)
  f.instance.choiceText.value = '5. marketing'
  const first = f.instance.chooseText()
  assert.equal(f.requests[0].action.choice_text, '5. marketing')
  assert.equal(f.requests[0].action.choice_id, undefined)
  assert.equal(f.requests[0].state.question.id, 'question-0')
  f.pending[0]({ ...sample(1), phase: 'sector' })
  await first
  assert.equal(f.instance.choiceText.value, '')
})

test('action and recovery failures are both visible, without replay', async t => {
  let actions = 0
  const f = fixture(t, {
    sendPreviewAction: async () => { actions++; throw Error('Action interrompue') },
    readPreview: async () => { throw Error('Connexion perdue') },
  })
  await f.instance.choose('marketing_visibilite')
  assert.match(f.instance.error.value, /Action interrompue/)
  assert.match(f.instance.error.value, /Récupération.*Connexion perdue/)
  assert.equal(actions, 1)
  assert.equal(f.instance.busy.value, false)
})

test('parcours URL binds session and revision, never the local need', t => {
  const f = fixture(t)
  f.instance.state.value = { ...sample(), phase: 'terminal', problem_original: 'besoin privé',
    card: { preview_parcours_url: '/preview/parcours/session-a?revision=4' } }
  assert.equal(f.instance.parcoursUrl.value, 'http://127.0.0.1:8767/preview/parcours/session-a?revision=4')
})

test('rejected choices and unchanged recovery preserve all uncommitted input', async t => {
  const f = fixture(t, { sendPreviewAction: async () => { throw Error('Choix inconnu') } })
  f.instance.initialNeed.value = 'Mes descriptions doivent rester factuelles.'
  f.instance.problem.value = 'Précision non encore envoyée.'
  f.instance.choiceText.value = '15'
  await f.instance.chooseText()
  assert.match(f.instance.error.value, /Choix inconnu/)
  assert.equal(f.instance.initialNeed.value, 'Mes descriptions doivent rester factuelles.')
  assert.equal(f.instance.problem.value, 'Précision non encore envoyée.')
  assert.equal(f.instance.choiceText.value, '15')
  await f.instance.refresh()
  assert.equal(f.instance.initialNeed.value, 'Mes descriptions doivent rester factuelles.')
  assert.equal(f.instance.choiceText.value, '15')
})

test('recovery installs a transition committed before a lost response', async t => {
  const f = fixture(t, {
    sendPreviewAction: async () => { throw Error('Réponse perdue') },
    readPreview: async () => ({ ...sample(1), phase: 'sector', initial_need: 'Besoin confirmé', problem_original: 'Besoin confirmé' }),
  })
  f.instance.initialNeed.value = 'Brouillon'
  f.instance.choiceText.value = '5'
  await f.instance.chooseText()
  assert.equal(f.instance.initialNeed.value, 'Besoin confirmé')
  assert.equal(f.instance.choiceText.value, '')
  assert.equal(f.instance.state.value.phase, 'sector')
})

test('only explicit loopback HTTP API origins are accepted', () => {
  assert.equal(apiExports.PREVIEW_ORIGIN, 'http://127.0.0.1:8767')
  assert.equal(apiExports.previewOrigin('http://localhost:8767'), 'http://localhost:8767')
  for (const origin of ['https://public.example', 'http://127.0.0.1:8767/path', 'http://user@localhost:8767',
    'http://127.0.0.1:8767?need=x', 'http://127.0.0.1:8767#need', 'http://localhost']) {
    assert.throws(() => apiExports.previewOrigin(origin))
  }
})

test('preview reuses AVIA blue/navy and Outfit fallback without a global theme mutation', () => {
  assert.match(component, /--cp-accent: #0969da/)
  assert.match(component, /--cp-bg: #0d1117/)
  assert.match(component, /prefers-color-scheme: dark/)
  assert.match(component, /font-family:'Outfit',-apple-system,BlinkMacSystemFont,"Segoe UI"/)
  assert.doesNotMatch(component, /#b11f4b|#fd8ea1|document\.documentElement|scoutTheme|laboratoire local/)
  assert.match(component, /A Vous l'IA — version de test/)
  assert.match(component, /<label v-if="!CLOUD_PREVIEW"/)
  assert.match(component, /<details v-if="state && phase === 'domain' && !state.initial_need"/)
})

test('public source discovery never starts an external session without consent', async t => {
  let creations = 0
  const f = fixture(t, {
    readPreviewSource: async () => ({ source_mode: 'PUBLIC_API', source_url: 'https://published.example' }),
    createPreview: async (_signal, consent) => {
      creations++
      assert.equal(consent, true)
      return { ...sample(), diagnostics: { source: { source_mode: 'PUBLIC_API' } } }
    },
  })

  f.instance.state.value = null
  await f.instance.initialize()
  assert.equal(creations, 0)
  assert.equal(f.instance.publicMode.value, true)
  await f.instance.start()
  assert.equal(creations, 0)
  assert.match(f.instance.error.value, /Confirmez/)
  f.instance.externalConsent.value = true
  await f.instance.start()
  assert.equal(creations, 1)
})

test('PUBLIC_PAGES requires consent and sends explicit mode without changing needs', async t => {
    let creations = 0
    const f = fixture(t, {
      readPreviewSource: async () => ({ source_mode: 'PUBLIC_PAGES' }),
      createPreview: async (_signal, consent, mode) => {
        creations++
        assert.equal(consent, true)
        assert.equal(mode, 'PUBLIC_PAGES')
        return { ...sample(), diagnostics: { source: { source_mode: 'PUBLIC_PAGES' } } }
      },
})
    f.instance.state.value = null
    await f.instance.initialize()
    await f.instance.start()
    assert.equal(creations, 0)
    assert.equal(f.instance.pagesMode.value, true)
    f.instance.externalConsent.value = true
    await f.instance.start()
    assert.equal(creations, 1)
  })

test('explicit source switch revokes previous consent and clears previous session', async t => {
    const f = fixture(t, { readPreviewSource: async () => ({ source_mode: 'PUBLIC_PAGES' }) })
    f.instance.externalConsent.value = true
    f.instance.selectedMode.value = 'PUBLIC_PAGES'
    await f.instance.changeSource()
    assert.equal(f.instance.state.value, null)
    assert.equal(f.instance.externalConsent.value, false)
    assert.match(component, /Ne saisissez aucune donnée personnelle ou confidentielle/)
    assert.match(component, /gpt-5-mini et text-embedding-3-small/)
})

test('unknown source fails closed without creating a session', async t => {
  let creations = 0
  const f = fixture(t, {
    readPreviewSource: async () => { throw Error('Source inconnue') },
    createPreview: async () => { creations++; return sample() },
  })
  f.instance.state.value = null
  f.instance.source.value = null
  await f.instance.initialize()
  assert.equal(creations, 0)
  assert.equal(f.instance.source.value, null)
  assert.match(f.instance.error.value, /Source inconnue/)
})

test('cloud API pins PUBLIC_PAGES and prevents requests without consent or to operator source modes', async () => {
  const calls = []
  const source = { source_mode: 'PUBLIC_PAGES', case_count: 1021, catalogue_version: 'v4.6.1' }
  const api = loadApi(cloudEnv, async (url, options) => {
    calls.push({ url, options })
    return { ok: true, json: async () => url.includes('/health') ? { source } : { ...sample(), diagnostics: { source } } }
  })
  await api.readPreviewSource()
  assert.equal(calls[0].url, `${backend}/health?source_mode=PUBLIC_PAGES`)
  await assert.rejects(api.createPreview(undefined, false), /Confirmez/)
  for (const mode of ['SYNTHETIC', 'PUBLIC_API']) {
    await assert.rejects(api.createPreview(undefined, true, mode), /uniquement/)
    await assert.rejects(api.readPreviewSource(undefined, mode), /uniquement/)
  }
  assert.equal(calls.length, 1)
  await api.createPreview(undefined, true)
  assert.equal(calls[1].url, `${backend}/api/preview/v1/sessions`)
  assert.deepEqual(JSON.parse(calls[1].options.body), {
    protocol_version: 1, external_consent: true, source_mode: 'PUBLIC_PAGES',
  })
  const wrongSource = loadApi(cloudEnv, async () => ({ ok: true, json: async () => ({ source: { source_mode: 'SYNTHETIC' } }) }))
  await assert.rejects(wrongSource.readPreviewSource(), /uniquement/)
})

test('cloud view never starts the fixture or PUBLIC_API source, and consent is a submission wall', async t => {
  let creations = 0
  const f = fixture(t, {
    CLOUD_PREVIEW: true,
    readPreviewSource: async () => ({ source_mode: 'PUBLIC_API' }),
    createPreview: async () => { creations++; return sample() },
  })
  f.instance.state.value = null
  f.instance.source.value = null
  assert.equal(f.instance.selectedMode.value, 'PUBLIC_PAGES')
  await f.instance.initialize()
  assert.match(f.instance.error.value, /Source inattendue/)
  assert.equal(creations, 0)
  assert.equal(f.instance.source.value, null)
  f.instance.state.value = { ...sample(), diagnostics: { source: { source_mode: 'PUBLIC_PAGES' } } }
  await f.instance.choose('marketing_visibilite')
  assert.equal(f.requests.length, 0)
  assert.match(f.instance.error.value, /Confirmez/)
  await f.instance.changeSource()
  assert.equal(f.instance.state.value.session_id, 'session-a')
})

test('preview privacy does not promise fast cloud latency or mutate the initial need from URL parameters', () => {
  assert.match(component, /des dizaines de secondes, parfois plusieurs minutes/)
  assert.match(component, /ne supprime pas cette attente/)
  assert.doesNotMatch(component, /URLSearchParams|window\.location\.search|query.*initialNeed/)
  assert.match(component, /const externalConsent = ref\(false\)/)
  const template = parse(component).descriptor.template.content
  const diagnostics = template.match(/<details class="diagnostics">[\s\S]*?<\/details>/)[0]
  assert.doesNotMatch(diagnostics, /<details[^>]*\bopen\b/)
  assert.equal(template.indexOf('class="options"') < template.indexOf('class="optional-need"'), true)
})

test('rendered cloud qualification keeps all server options; terminal is one CTA with no input', async t => {
  const f = fixture(t, { CLOUD_PREVIEW: true, env: { BASE_URL: '/A-Vous-l-IA/' } })
  const source = { source_mode: 'PUBLIC_PAGES', case_count: 1021, catalogue_version: 'v4.6.1' }
  const options = Array.from({ length: 14 }, (_, index) => ({
    id: `canonical-domain-${index + 1}`, label: `Domaine source ${index + 1}`, number: index + 1,
  }))
  f.instance.state.value = { ...sample(), question: { id: 'question-0', prompt: 'Votre domaine ?', options }, diagnostics: { source } }
  const render = () => renderToString(vue.createSSRApp({
    setup: () => f.instance, render: vue.compile(parse(component).descriptor.template.content),
  }))
  const domain = await render()
  for (const option of options) assert.ok(domain.includes(`${option.number}. ${option.label}`))
  assert.equal((domain.match(/class="option"/g) || []).length, 14)
  assert.doesNotMatch(domain, /<select|SYNTHETIC|PUBLIC_API/)
  assert.match(domain, /href="\/A-Vous-l-IA\/"/)
  f.instance.state.value = {
    ...sample(7), phase: 'terminal', diagnostics: { source },
    card: { case_id: 'case-a', title: 'Titre source', description: 'Description source.',
      preview_parcours_url: '/preview/parcours/session-a?revision=7', source_hash: 'test',
      source_url: 'https://published.example/case-a', handoff_url: '/api/preview/v1/sessions/session-a/handoff' },
  }
  const terminal = await render()
  assert.equal((terminal.match(/class="primary link"/g) || []).length, 1)
  assert.match(terminal, /preview\/parcours\/session-a\?revision=7/)
  assert.doesNotMatch(terminal, /<(?:textarea|input|select|form)\b/)
  assert.match(terminal, /<details class="source-details">/)
  assert.match(terminal, /<details class="diagnostics">/)
})

test('public mode explains external treatment, old retrieval and published parcours without fake coverage', () => {
  assert.match(component, /Traitement et journalisation possibles/)
  assert.match(component, /Le RAG existant n'est pas corrigé/)
  assert.match(component, /Orientation transversale indisponible/)
  assert.match(component, /Ouvrir le parcours actuel publié/)
  assert.match(component, /aucun contexte dans les liens/)
  assert.equal((component.match(/class="primary link"/g) || []).length, 1)
})

test('PUBLIC_PAGES has one local primary CTA and its published source only in collapsed provenance', t => {
  const f = fixture(t)
  f.instance.state.value = { ...sample(7), phase: 'terminal',
    problem_original: 'SYNTHETIC besoin exact, sans WhatsApp',
    card: {
      preview_parcours_url: '/preview/parcours/session-a?revision=7',
      source_url: 'https://published.example/action-synthetic.html',
      parcours_render_policy: 'public-neutral-v1',
    },
    diagnostics: { source: { source_mode: 'PUBLIC_PAGES' } },
  }
  assert.equal(f.instance.pagesMode.value, true)
  assert.equal(f.instance.publicMode.value, false)
  assert.equal(f.instance.parcoursUrl.value, 'http://127.0.0.1:8767/preview/parcours/session-a?revision=7')
  assert.doesNotMatch(f.instance.parcoursUrl.value, /besoin|WhatsApp|published/)
  const template = parse(component).descriptor.template.content
  const primary = template.match(/<a class="primary link"[\s\S]*?<\/a>/g)
  assert.equal(primary.length, 1)
  assert.match(primary[0], /publicMode \? 'Ouvrir le parcours actuel publié' : 'Ouvrir le parcours de test'/)
  assert.match(primary[0], /:href="parcoursUrl"/)
  const provenance = template.match(/<details class="source-details"[\s\S]*?<\/details>/)[0]
  assert.doesNotMatch(provenance, /\bopen(?:\s|>)/)
  assert.match(provenance, /Page source publiée/)
  assert.match(provenance, /:href="state.card.source_url"/)
  assert.doesNotMatch(template.replace(provenance, ''), /:href="state.card.source_url"/)
  assert.match(component, /textes déjà publiés v4.6.1 sont inchangés/)
  assert.match(component, /mode d'exécution non publié reste inconnu/)
  assert.match(component, /Copier ajoute le contexte et les règles seulement sur clic/)
  assert.match(component, /L'accord RAG n'autorise aucun nouvel envoi depuis le parcours/)
})
