import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { runInNewContext } from 'node:vm'
import * as vue from 'vue'
import { parse } from 'vue/compiler-sfc'
import ts from 'typescript'

// Exercise the real setup script with lifecycle/network mocks, without a DOM or backend.
const homeSource = readFileSync(new URL('../src/views/HomeView.vue', import.meta.url), 'utf8')
const setup = parse(homeSource).descriptor.scriptSetup.content
  .replace(/import \{([^}]+)\} from 'vue'/, 'const {$1} = vue')
  .replace(/import \{([^}]+)\} from '@\/api\/chat'/, 'const {$1} = api')
const expose = `
return { submit, goBackToStep, messages, loading, currentPhase, showStepper, steps, selectedDomainCode,
  selectedSector, selectedIntention, lastSuggestedCases, pendingAction, pendingUseCaseId }
`
const createSetup = new Function('vue', 'api', setup + expose)

function fixture(t) {
  let callbacks
  let finish
  const requests = []
  const scope = vue.effectScope()
  t.after(() => scope.stop())
  const home = scope.run(() => createSetup(
    { ...vue, onMounted: () => {} },
    {
      sendMessageStream: async (request, handlers) => {
        requests.push(request)
        callbacks = handlers
        await new Promise(resolve => { finish = resolve })
      },
    },
  ))
  home.messages.value = [
    { role: 'assistant', content: 'Dans quel domaine travaillez-vous ?' },
    { role: 'user', content: '13' },
    { role: 'assistant', content: 'Dans quel secteur travaillez-vous ?' },
    { role: 'user', content: 'BTP' },
    { role: 'assistant', content: 'Quel est votre objectif principal ?' },
  ]
  home.selectedDomainCode.value = 'activites_terrain'
  home.selectedSector.value = 'BTP'
  home.selectedIntention.value = 'gagner_du_temps'
  return {
    home, requests,
    token: text => callbacks.onToken(text),
    done: payload => { callbacks.onDone({ sources: [], ...payload }); finish() },
    error: message => { callbacks.onError(message); finish() },
  }
}

function state(home) {
  return [home.selectedDomainCode.value, home.selectedSector.value, home.selectedIntention.value]
}

const cases = [
  ['combined domain/sector/intention stays authoritative',
    { selected_domain_code: 'nouveau_domaine', selected_sector: 'nouveau_secteur', selected_intention: 'nouvel_objectif' },
    ['nouveau_domaine', 'nouveau_secteur', 'nouvel_objectif']],
  ['unchanged domain retains supplied sector and intention',
    { selected_domain_code: 'activites_terrain', selected_sector: 'nouveau_secteur', selected_intention: 'nouvel_objectif' },
    ['activites_terrain', 'nouveau_secteur', 'nouvel_objectif']],
  ['changed domain invalidates omitted dependents',
    { selected_domain_code: 'nouveau_domaine' }, ['nouveau_domaine', null, null]],
  ['changed sector invalidates omitted intention',
    { selected_sector: 'nouveau_secteur' }, ['activites_terrain', 'nouveau_secteur', null]],
  ['omitted fields preserve unchanged state',
    {}, ['activites_terrain', 'BTP', 'gagner_du_temps']],
  ['unchanged parent preserves omitted dependents',
    { selected_domain_code: 'activites_terrain', selected_sector: 'BTP' },
    ['activites_terrain', 'BTP', 'gagner_du_temps']],
  ['explicit null domain clears omitted dependents',
    { selected_domain_code: null }, [null, null, null]],
  ['explicit null sector clears omitted intention',
    { selected_sector: null }, ['activites_terrain', null, null]],
  ['explicit null intention is not ignored',
    { selected_intention: null }, ['activites_terrain', 'BTP', null]],
  ['early explicit sector survives domain selection response',
    { selected_domain_code: 'nouveau_domaine', selected_sector: 'BTP', selected_intention: null },
    ['nouveau_domaine', 'BTP', null]],
]

for (const [name, payload, expected] of cases) {
  test(name, async t => {
    const f = fixture(t)
    const first = f.home.submit('13')
    await vue.nextTick()
    f.done(payload)
    await first
    assert.deepEqual(state(f.home), expected)
    const second = f.home.submit('suite')
    await vue.nextTick()
    assert.deepEqual([
      f.requests[1].selected_domain_code ?? null,
      f.requests[1].selected_sector ?? null,
      f.requests[1].selected_intention ?? null,
    ], expected, 'next request must carry the resolved qualification')
    f.done({})
    await second
  })
}

test('submission locks immediately; rewind and duplicate submission cannot disturb in-flight tokens', async t => {
  const f = fixture(t)
  const first = f.home.submit('13')
  assert.equal(f.home.loading.value, true)
  const messages = f.home.messages.value
  f.home.goBackToStep(0)
  assert.equal(f.home.messages.value, messages)
  await f.home.submit('duplicate')
  await vue.nextTick()
  assert.equal(f.requests.length, 1)
  f.token('Quel est votre objectif principal ?')
  f.home.goBackToStep(0)
  assert.equal(f.home.messages.value.length, 7)
  f.done({})
  await first
  assert.equal(f.home.messages.value.at(-1).content, 'Quel est votre objectif principal ?')
  assert.equal(f.home.loading.value, false)
  f.home.goBackToStep(0)
  assert.equal(f.home.messages.value.length, 1)
  assert.deepEqual(state(f.home), [null, null, null])
})

test('stream error unlocks rewind', async t => {
  const f = fixture(t)
  const pending = f.home.submit('13')
  await vue.nextTick()
  f.error('synthetic stream failure')
  await pending
  assert.equal(f.home.loading.value, false)
  f.home.goBackToStep(0)
  assert.equal(f.home.messages.value.length, 1)
})

test('no-match keeps previous steps available without selectable case buttons', async t => {
  const f = fixture(t)
  const pending = f.home.submit('Besoin sans correspondance')
  await vue.nextTick()
  f.token("Je n'ai pas de cas suffisamment pertinent à vous proposer avec les choix actuels. Vous pouvez préciser votre besoin ou revenir à une étape précédente pour modifier vos choix.")
  f.done({ suggested_cases: [], pending_action: null, pending_use_case_id: null })
  await pending
  assert.equal(f.home.showStepper.value, true)
  assert.equal(f.home.currentPhase.value, 3)
  assert.equal(f.home.steps.value[0].state, 'done')
  assert.equal(f.home.steps.value[4].state, 'upcoming')
  assert.deepEqual(f.home.lastSuggestedCases.value, [])
  f.home.goBackToStep(0)
  assert.deepEqual(state(f.home), [null, null, null])
})

const apiSource = readFileSync(new URL('../src/api/chat.ts', import.meta.url), 'utf8')
  .replace('import.meta.env.VITE_API_URL', '"http://mock.invalid/api/v1"')
const compiledApi = ts.transpileModule(apiSource, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText

for (const trailingNewline of [true, false]) {
  for (const payload of [
    { selected_domain_code: 'activites_terrain', selected_sector: 'BTP', selected_intention: 'gagner_du_temps' },
    {},
    { selected_domain_code: null, selected_sector: null, selected_intention: null },
  ]) {
    test(`SSE preserves absent/null/combined qualification ${JSON.stringify(payload)} (newline=${trailingNewline})`, async () => {
      const exports = {}
      const body = `data: ${JSON.stringify({ done: true, ...payload })}${trailingNewline ? '\n\n' : ''}`
      runInNewContext(compiledApi, {
        exports, TextDecoder,
        fetch: async url => {
          assert.equal(url, 'http://mock.invalid/api/v1/chat/stream')
          return new Response(body)
        },
      })
      let result
      await exports.sendMessageStream({ message: 'synthetic', history: [] }, {
        onToken: () => assert.fail('unexpected token'),
        onError: message => assert.fail(message),
        onDone: value => { result = value },
      })
      for (const key of ['selected_domain_code', 'selected_sector', 'selected_intention']) {
        assert.equal(result[key], payload[key], key)
      }
    })
  }
}
