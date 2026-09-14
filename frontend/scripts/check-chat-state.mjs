import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { runInNewContext } from 'node:vm'
import * as vue from 'vue'
import { parse } from 'vue/compiler-sfc'
import ts from 'typescript'

// Exercise the real setup script with lifecycle/network mocks, without a DOM or backend.
const homeSource = readFileSync(new URL('../src/views/HomeView.vue', import.meta.url), 'utf8')
test('homepage figures match the consolidated catalogue and distinguish domains from sectors', () => {
  assert.match(homeSource, /class="stat-number">1&nbsp;021<\/div>/)
  assert.match(homeSource, /class="stat-number">14<\/div>\s*<div class="stat-label">Domaines m&eacute;tier<\/div>/)
  assert.doesNotMatch(homeSource, /1&nbsp;025|Secteurs couverts/)
})
const setup = parse(homeSource).descriptor.scriptSetup.content
  .replace(/import \{([^}]+)\} from 'vue'/, 'const {$1} = vue')
  .replace(/import \{([^}]+)\} from '@\/api\/chat'/, 'const {$1} = api')
const expose = `
return { submit, goBackToStep, messages, loading, currentPhase, showStepper, steps, selectedDomainCode,
  selectedSector, selectedIntention, lastSuggestedCases, pendingAction, pendingUseCaseId, choicesFor, lastAssistantIndex,
  failedTurn, error, retryLastRequest, selectedValue }
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
  assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)), [])
  f.home.goBackToStep(0)
  assert.deepEqual(state(f.home), [null, null, null])
})

const stockCase = {
  id: 'UC-SYNTHETIC-STOCK',
  content: 'Cas fictif pour tester la selection.',
  cas_utilisation: 'Analyser les invendus',
  parcours_url: 'https://example.test/action-stock.html',
}
const followupCase = {
  id: 'UC-SYNTHETIC-FOLLOWUP',
  content: 'Autre cas fictif.',
  cas_utilisation: 'Suivre les actions',
  parcours_url: 'https://example.test/action-followup.html',
}

for (const text of [
  '1. Analyser les invendus\nPourquoi : comprendre la faible rotation.\nIndiquez son numéro.',
  '**1. Analyser les invendus**\nPourquoi : comprendre la faible rotation.',
  'Voici le cas adapté : Analyser les invendus.',
]) {
  test(`single case is selectable from server metadata, independent of Markdown: ${text.split('\n')[0]}`, async t => {
    const f = fixture(t)
    const list = f.home.submit('Je souhaite comprendre les invendus.')
    await vue.nextTick()
    f.token(text)
    f.done({ suggested_cases: [stockCase], suggested_case_ids: [stockCase.id] })
    await list
    const msg = f.home.messages.value.at(-1)
    const choices = f.home.choicesFor(msg)
    assert.deepEqual(choices, [{
      num: 1, label: 'Choisir ce cas', accessibleLabel: 'Choisir le cas 1 : Analyser les invendus',
    }])
    assert.equal(msg.parcoursUrl, null, 'candidate URL is not yet a parcours CTA')
    assert.equal(f.home.currentPhase.value, 4)
    const detail = f.home.submit(String(choices[0].num))
    await vue.nextTick()
    assert.equal(f.requests[1].message, '1')
    assert.deepEqual(f.requests[1].last_suggested_cases.map(c => c.id), [stockCase.id])
    f.token('Ce que ça vous apporte : une analyse des invendus.')
    f.done({ suggested_cases: [stockCase], parcours_url: stockCase.parcours_url })
    await detail
    assert.equal(f.home.messages.value.at(-1).parcoursUrl, stockCase.parcours_url)
    assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)), [])
    assert.equal(f.home.currentPhase.value, 5)
    f.home.goBackToStep(4)
    assert.equal(f.home.choicesFor(f.home.messages.value.at(-1)).length, 1)
    assert.equal(f.home.currentPhase.value, 4)
  })
}

test('rewinding from a detail restores the original selectable cases and their order', async t => {
  const f = fixture(t)
  const list = f.home.submit('Besoin fictif')
  await vue.nextTick()
  f.token('**1. Analyser les invendus**\nDescription.\n**2. Suivre les actions**\nDescription.')
  f.done({ suggested_cases: [stockCase, followupCase] })
  await list
  assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)).map(c => c.label), ['Cas 1', 'Cas 2'])
  const firstDetail = f.home.submit('1')
  await vue.nextTick()
  f.token('Ce que ça vous apporte : analyse.')
  f.done({ suggested_cases: [stockCase], parcours_url: stockCase.parcours_url })
  await firstDetail
  f.home.goBackToStep(4)
  assert.deepEqual(f.home.lastSuggestedCases.value.map(c => c.id), [stockCase.id, followupCase.id])
  const secondDetail = f.home.submit('2')
  await vue.nextTick()
  assert.deepEqual(f.requests[2].last_suggested_cases.map(c => c.id), [stockCase.id, followupCase.id])
  f.token('Ce que ça vous apporte : suivi.')
  f.done({ suggested_cases: [followupCase], parcours_url: followupCase.parcours_url })
  await secondDetail
  assert.equal(f.home.messages.value.at(-1).parcoursUrl, followupCase.parcours_url)
})

for (const content of [
  'Pouvez-vous décrire le problème concret ?\n1. Délais\n2. Erreurs',
  "Je n'ai pas de cas suffisamment pertinent avec les choix actuels.\n1. Précisez votre besoin\n2. Changez de domaine",
  'Ce que ça vous apporte\n1. Un résultat\n2. Une action',
  '1. Un titre sans identité serveur\nDescription.\n2. Un autre titre\nDescription.',
]) {
  test(`numbered non-case content does not create selectable cases: ${content.split('\n')[0]}`, async t => {
    const f = fixture(t)
    const pending = f.home.submit('suite')
    await vue.nextTick()
    f.token(content)
    f.done({ suggested_cases: [] })
    await pending
    assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)), [])
  })
}

test('detail without a mapped parcours still does not offer its single case for selection', async t => {
  const f = fixture(t)
  const pending = f.home.submit('1')
  await vue.nextTick()
  f.token('Ce que ça vous apporte : un résultat utile.')
  f.done({ suggested_cases: [stockCase] })
  await pending
  assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)), [])
  assert.equal(f.home.currentPhase.value, 5)
})

test('guided menus retain their labels and rewinding to qualification clears cases', async t => {
  const f = fixture(t)
  f.home.messages.value.at(-1).content = 'Quel est votre objectif principal ?\n1. Synthétiser\n2. Organiser'
  assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)), [
    { num: 1, label: 'Synthétiser' }, { num: 2, label: 'Organiser' },
  ])
  const pending = f.home.submit('1')
  await vue.nextTick()
  f.token('1. Analyser les invendus\nDescription.')
  f.done({ suggested_cases: [stockCase] })
  await pending
  f.home.goBackToStep(2)
  assert.equal(f.home.lastSuggestedCases.value, null)
  assert.deepEqual(f.home.choicesFor(f.home.messages.value.at(-1)).map(c => c.label), ['Synthétiser', 'Organiser'])
})

test('case chips are wired to message metadata and hidden on older or streaming messages', () => {
  assert.match(homeSource, /i === lastAssistantIndex && !loading && choicesFor\(msg\)\.length/)
  assert.match(homeSource, /v-for="c in choicesFor\(msg\)"/)
  assert.match(homeSource, /@click="submit\(String\(c\.num\)\)"/)
})

const apiSource = readFileSync(new URL('../src/api/chat.ts', import.meta.url), 'utf8')
  .replace('import.meta.env.VITE_API_URL', '"http://mock.invalid/api/v1"')
const compiledApi = ts.transpileModule(apiSource, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText

test('retry preserves the exact failed request without duplicating conversation turns', async t => {
  const f = fixture(t)
  const before = f.home.messages.value.length
  const pending = f.home.submit('Besoin à conserver')
  await vue.nextTick()
  const request = JSON.stringify(f.requests[0])
  f.token('Réponse partielle')
  f.error('Connexion interrompue')
  await pending
  assert.equal(f.home.messages.value.length, before + 1)
  assert.equal(f.home.messages.value.at(-1).role, 'user')
  assert.equal(f.home.failedTurn.value.request.message, 'Besoin à conserver')
  const retry = f.home.retryLastRequest()
  await vue.nextTick()
  await f.home.retryLastRequest()
  assert.equal(f.requests.length, 2)
  assert.equal(JSON.stringify(f.requests[1]), request)
  f.token('Réponse confirmée')
  f.done({})
  await retry
  assert.equal(f.home.messages.value.length, before + 2)
  assert.equal(f.home.error.value, null)
  assert.equal(f.home.failedTurn.value, null)
})

test('rewind discards retry and selected value follows the authoritative URL only', async t => {
  const f = fixture(t)
  const pending = f.home.submit('Besoin')
  await vue.nextTick()
  f.error('Échec')
  await pending
  f.home.goBackToStep(0)
  assert.equal(f.home.failedTurn.value, null)
  const value = { version: 'source-value-1', description: '<script>source non HTML</script>' }
  assert.equal(f.home.selectedValue({ suggestedCases: [{ ...stockCase, value_presentation: value }] }), null)
  assert.deepEqual(f.home.selectedValue({
    parcoursUrl: stockCase.parcours_url, suggestedCases: [{ ...stockCase, value_presentation: value }],
  }), value)
  assert.doesNotMatch(homeSource, /v-html/)
  assert.match(homeSource, /v-for="\(c, ci\) in msg.suggestedCases"/)
})

for (const body of ['', 'data: {"t":"partiel"}\n\n', 'data: {"bad":true}', 'data: invalid']) {
  test(`incomplete SSE is never acknowledged as success: ${body}`, async () => {
    const exports = {}
    runInNewContext(compiledApi, { exports, TextDecoder, fetch: async () => new Response(body) })
    let errors = 0
    await exports.sendMessageStream({ message: 'synthetic', history: [] }, {
      onToken: () => {},
      onDone: () => assert.fail('incomplete stream cannot succeed'),
      onError: () => { errors++ },
    })
    assert.equal(errors, 1)
  })
}

test('welcome adds only the canonical server question; fallback invents no choices', async () => {
  const exports = {}
  runInNewContext(compiledApi, { exports, TextDecoder, fetch: async () => Response.json({
    message: 'Bonjour', initial_question: 'Dans quel domaine ?\n1. Domaine exact\n2. Autre domaine',
  }) })
  assert.equal(await exports.getWelcomeMessage(), 'Bonjour\n\nDans quel domaine ?\n1. Domaine exact\n2. Autre domaine')
})

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
