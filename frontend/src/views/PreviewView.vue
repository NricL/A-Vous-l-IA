<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  acceptsResponse, createPreview, CLOUD_PREVIEW, PREVIEW_ORIGIN, readPreview, readPreviewSource, sendPreviewAction,
  type Phase, type PreviewAction, type PreviewSource, type PreviewState,
} from '@/api/preview'

const state = ref<PreviewState | null>(null)
const busy = ref(false)
const error = ref('')
const initialNeed = ref('')
const problem = ref('')
const choiceText = ref('')
const source = ref<PreviewSource | null>(null)
const externalConsent = ref(false)
const publicMode = computed(() => (state.value?.diagnostics.source ?? source.value)?.source_mode === 'PUBLIC_API')
const pagesMode = computed(() => (state.value?.diagnostics.source ?? source.value)?.source_mode === 'PUBLIC_PAGES')
const externalMode = computed(() => publicMode.value || pagesMode.value)
const selectedMode = ref<PreviewSource['source_mode'] | undefined>(CLOUD_PREVIEW ? 'PUBLIC_PAGES' : undefined)
const homeUrl = import.meta.env.BASE_URL
const labels: Record<Phase, string> = {
  domain: 'Domaine', sector: 'Secteur', objective: 'Objectif', problem: 'Problème',
  results: 'Cas', orientation: 'Orientation proposée', terminal: 'Fiche',
}
let epoch = 0
let controller: AbortController | null = null
let previousTitle = ''
const phase = computed(() => state.value?.phase ?? 'domain')
const prompt = computed(() => state.value?.question.prompt ?? 'Dans quel domaine souhaitez-vous avancer ?')
const parcoursUrl = computed(() => state.value?.card
  ? `${PREVIEW_ORIGIN}${state.value.card.preview_parcours_url}` : '')
const currentSource = computed(() => state.value?.diagnostics.source ?? source.value)
const selections = computed(() => [
  { target: 'domain' as Phase, label: state.value?.confirmed.domain_label },
  { target: 'sector' as Phase, label: state.value?.confirmed.sector },
  { target: 'objective' as Phase, label: state.value?.confirmed.objective_label },
].filter(selection => selection.label))
function retrievalDiagnostic(result: PreviewState['diagnostics']['main']) {
  if (!result) return null
  return {
    filters: result.filters_applied, eligible_count: result.details?.eligible_count,
    candidates_ranked: result.details?.ranked_candidates ?? result.candidate_ids,
    retained_ids: result.result_ids, engine: result.engine,
    context_budget_omitted: result.details?.context_budget_omitted,
    all_bounded_candidates_sent: result.details?.all_bounded_candidates_sent,
    model: result.details?.model_usage,
  }
}
const diagnostics = computed(() => JSON.stringify({
  phase: state.value?.phase, revision: state.value?.revision,
  question_id: state.value?.question.id, confirmed: state.value?.confirmed,
  main: retrievalDiagnostic(state.value?.diagnostics.main ?? null),
  orientation: retrievalDiagnostic(state.value?.diagnostics.orientation ?? null),
  source: {
    mode: state.value?.diagnostics.source.source_mode,
    version: state.value?.diagnostics.source.catalogue_version,
    count: state.value?.diagnostics.source.case_count,
    coverage: state.value?.diagnostics.source.coverage,
    engine: state.value?.diagnostics.source.retrieval_engine,
  },
}, null, 2))

function beginRequest() {
  controller?.abort()
  controller = new AbortController()
  busy.value = true
  error.value = ''
  return { ticket: ++epoch, signal: controller.signal }
}

function install(next: PreviewState, preserveDrafts = false) {
  const unchanged = state.value?.session_id === next.session_id
    && state.value.revision === next.revision
  state.value = next
  if (preserveDrafts && unchanged) return
  problem.value = next.problem_original
  initialNeed.value = next.initial_need
  choiceText.value = ''
}

async function start() {
  if (!source.value) {
    error.value = "Vérifiez d'abord la source de cette version de test."
    return
  }
  if ((CLOUD_PREVIEW || externalMode.value) && !externalConsent.value) {
    error.value = "Confirmez d'abord l'envoi aux modèles Azure pour cette session."
    return
  }
  const { ticket, signal } = beginRequest()
  try {
    const next = await createPreview(signal, externalConsent.value, selectedMode.value)
    if (ticket === epoch) install(next)
  } catch (cause) {
    if (ticket === epoch) error.value = cause instanceof Error ? cause.message : 'Serveur de test indisponible.'
  } finally {
    if (ticket === epoch) busy.value = false
  }
}

async function initialize() {
  const { ticket, signal } = beginRequest()
  try {
    const currentSource = await readPreviewSource(signal, selectedMode.value)
    if (ticket !== epoch) return
    if (CLOUD_PREVIEW && currentSource.source_mode !== 'PUBLIC_PAGES') {
      throw new Error('Source inattendue : cette version de test exige les pages publiques v4.6.1.')
    }
    source.value = currentSource
    selectedMode.value = currentSource.source_mode
    busy.value = false
    if (currentSource.source_mode === 'SYNTHETIC') await start()
  } catch (cause) {
    if (ticket === epoch) error.value = cause instanceof Error ? cause.message : 'Source indisponible.'
  } finally {
    if (ticket === epoch) busy.value = false
  }
}

async function changeSource() {
  if (CLOUD_PREVIEW) return
  state.value = null
  source.value = null
  externalConsent.value = false
  initialNeed.value = problem.value = choiceText.value = ''
  await initialize()
}

async function submit(action: PreviewAction) {
  // Button double clicks do not create a second command. Server revision guards
  // remain authoritative for retries, another tab and delayed responses.
  if (!state.value || busy.value) return
  if ((CLOUD_PREVIEW || externalMode.value) && !externalConsent.value) {
    error.value = "Confirmez d'abord l'envoi aux modèles Azure pour cette session."
    return
  }
  const before = state.value
  const { ticket, signal } = beginRequest()
  try {
    const next = await sendPreviewAction(before, action, crypto.randomUUID(), signal)
    if (ticket === epoch && acceptsResponse(state.value, next, before.session_id)) install(next)
  } catch (cause) {
    if (ticket === epoch) {
      error.value = cause instanceof Error ? cause.message : 'Réponse interrompue.'
      // Never replay an uncertain action automatically. Read the committed
      // state instead, so loss of the response cannot resurrect an old choice.
      try {
        const latest = await readPreview(before.session_id, signal)
        if (ticket === epoch && acceptsResponse(state.value, latest, before.session_id)) install(latest, true)
      } catch (recoveryCause) {
        if (ticket === epoch) {
          const message = recoveryCause instanceof Error ? recoveryCause.message : 'Serveur de test indisponible.'
          error.value += ` Récupération de l'état confirmé impossible : ${message}`
        }
      }
    }
  } finally {
    if (ticket === epoch) busy.value = false
  }
}

async function refresh() {
  if (!state.value) return source.value ? start() : initialize()
  const session = state.value.session_id
  const { ticket, signal } = beginRequest()
  try {
    const latest = await readPreview(session, signal)
    if (ticket === epoch && acceptsResponse(state.value, latest, session)) install(latest, true)
  } catch (cause) {
    if (ticket === epoch) error.value = cause instanceof Error ? cause.message : 'Session indisponible.'
  } finally {
    if (ticket === epoch) busy.value = false
  }
}

function choose(id: string) {
  const action: PreviewAction = { action: 'choose', choice_id: id }
  if (phase.value === 'domain' && !state.value?.initial_need) action.initial_need = initialNeed.value
  return submit(action)
}

function chooseText() {
  const action: PreviewAction = { action: 'choose', choice_text: choiceText.value }
  if (phase.value === 'domain' && !state.value?.initial_need) action.initial_need = initialNeed.value
  return submit(action)
}

onMounted(() => {
  previousTitle = document.title
  document.title = "A Vous l'IA — version de test"
  initialize()
})
onBeforeUnmount(() => {
  ++epoch
  controller?.abort()
  document.title = previousTitle
})
</script>

<template>
  <main class="preview">
    <header>
      <a class="brand" :href="homeUrl" aria-label="A Vous l'IA — accueil habituel">A Vous <span>l'IA</span><small>AVIA</small></a>
      <a :href="homeUrl" class="stable-link">Revenir au site habituel →</a>
    </header>
    <p class="test-banner"><strong>Version de test</strong> Un espace distinct : le site habituel ne change pas.</p>
    <section class="intro">
      <h1>Trouvez un usage de l'IA adapté à votre besoin.</h1>
      <p>Une question à la fois, un cas à choisir, puis un parcours pour passer à l'action.</p>
      <p class="source-proof" v-if="pagesMode">Source publique · {{ currentSource?.case_count }} cas · v4.6.1 <span>Aucun document privé ni contenu v4.6.2.</span></p>
      <p class="source-proof" v-else-if="publicMode">API publique existante · couverture complète non vérifiée.</p>
      <p class="source-proof" v-else-if="source">SYNTHÉTIQUE · NON PRODUCTION — {{ currentSource?.case_count }} cas fictifs, pas le RAG réel.</p>
      <p class="source-proof" v-else>Vérification de la source publique…</p>
    </section>
    <section class="workspace" aria-label="Qualification AVIA">
      <article :aria-busy="busy">
        <div class="phase-row"><span class="phase">{{ labels[phase] }}</span><span v-if="busy" role="status">Chargement… merci de patienter.</span></div>
        <nav v-if="selections.length" class="selections" aria-label="Vos choix confirmés, modifiables">
          <button v-for="selection in selections" :key="selection.target"
            :disabled="busy || !state?.back_targets.includes(selection.target)"
            @click="submit({ action: 'back', target: selection.target })">
            {{ labels[selection.target] }} : <strong>{{ selection.label }}</strong>
            <span v-if="state?.back_targets.includes(selection.target)" aria-hidden="true">✎</span>
          </button>
        </nav>
        <h2>{{ prompt }}</h2>
        <div v-if="error" class="error" role="alert">
          <p>{{ error }}</p><button :disabled="busy" @click="refresh">Recharger l'état confirmé</button>
          <button v-if="source" :disabled="busy" @click="start">Nouvelle session</button>
        </div>
        <p v-if="state?.warning" class="secondary-note" role="status">{{ state.warning }}</p>
        <section v-if="externalMode && !state" class="offer">
          <h3>Avant de commencer</h3>
          <p v-if="pagesMode">Votre besoin et les champs des cas publics seront envoyés aux modèles Azure OpenAI existants (gpt-5-mini et text-embedding-3-small) pour la recherche.</p>
          <p v-else>Votre besoin et vos choix seront envoyés à l'API AVIA publique et à son RAG existant pour la recherche.</p>
          <p><strong>Ne saisissez aucune donnée personnelle ou confidentielle.</strong> Traitement et journalisation possibles côté service Azure.</p>
          <label class="consent"><input v-model="externalConsent" type="checkbox" :disabled="busy" /> <span>J'accepte cet envoi pour cette session de test.</span></label>
          <button class="primary" :disabled="busy || !externalConsent" @click="start">Commencer</button>
        </section>
        <div v-if="['domain', 'sector', 'objective', 'results'].includes(phase)" class="options" :class="{ domains: phase === 'domain' }">
          <button v-for="option in state?.question.options ?? []" :key="option.id" :disabled="busy" class="option" @click="choose(option.id)">
            {{ option.number }}. {{ option.label }}<span aria-hidden="true">→</span>
          </button>
        </div>
        <details v-if="state && phase === 'domain' && !state.initial_need" class="optional-need">
          <summary>Ajouter un besoin déjà formulé (facultatif)</summary>
          <label class="problem-label">Votre besoin
            <textarea v-model="initialNeed" :disabled="busy" maxlength="8000" rows="2" placeholder="Votre formulation sera conservée, y compris les exclusions." />
          </label>
        </details>
        <form v-if="['domain', 'sector', 'objective', 'results'].includes(phase) && state?.question.options.length" class="choice-input" @submit.prevent="chooseText">
          <label for="preview-choice">Ou un numéro / libellé proposé</label>
          <div><input id="preview-choice" v-model="choiceText" :disabled="busy" maxlength="500" autocomplete="off" /><button :disabled="busy || !choiceText.trim()">Valider</button></div>
        </form>
        <form v-if="phase === 'problem'" @submit.prevent="submit({ action: 'describe', text: problem })">
          <label class="problem-label">Votre besoin, avec vos contraintes et exclusions
            <textarea v-model="problem" :disabled="busy" rows="4" maxlength="8000" required />
          </label>
          <button class="primary" :disabled="busy || !problem.trim()">Rechercher dans mes choix</button>
        </form>
        <template v-if="phase === 'orientation'">
          <p class="secondary-note">Recherche d'orientation séparée. Vos choix actuels et les filtres principaux n'ont pas changé.</p>
          <div v-for="option in state?.question.options" :key="option.id" class="offer">
            <p class="eyebrow">{{ externalMode ? 'Cas publié' : 'Cas fictif' }} {{ option.case_id }}</p><h3>{{ option.label }}</h3>
            <p><strong>{{ option.domain_label }}</strong><br>{{ option.objective_label }}</p>
            <p>Secteurs du cas source : {{ option.source_sectors?.join(', ') }}.</p>
            <p v-if="option.sector_revalidation_required">Le secteur sera demandé et l'objectif devra être revalidé avant toute recherche.</p>
            <p v-else>Secteur conservé : {{ option.sector ?? 'sans question secteur' }}.</p>
            <button class="primary" :disabled="busy" @click="submit({ action: 'accept', choice_id: option.id })">Confirmer cette orientation</button>
          </div>
          <button class="quiet" :disabled="busy" @click="submit({ action: 'refuse' })">Refuser et garder mes choix</button>
        </template>
        <section v-if="state?.card" class="case-card">
          <p class="eyebrow">{{ externalMode ? 'Cas issu de la source publique' : 'Cas fictif' }} · {{ state.card.case_id }}</p>
          <h3>{{ state.card.title }}</h3><p>{{ state.card.description }}</p>
          <a class="primary link" :href="parcoursUrl" target="_blank" rel="noopener noreferrer">{{ publicMode ? 'Ouvrir le parcours actuel publié' : 'Ouvrir le parcours de test' }}</a>
          <p v-if="publicMode" class="secondary-note">Page publique existante, pas le nouveau template local. Aucun besoin ajouté au lien ou transmis à cette page ; ses propres services externes peuvent s'appliquer après ouverture.</p>
          <p v-else-if="pagesMode" class="secondary-note">Un parcours de test en six étapes, à partir des textes publics v4.6.1. Vous choisissez ensuite quoi copier et où le coller.</p>
          <details class="source-details"><summary>Provenance du cas</summary>
            <p>Source : {{ state.diagnostics.source.catalogue_version }} ({{ state.diagnostics.source.source_mode }})</p>
            <p class="hash">SHA-256 : {{ state.card.source_hash }}</p>
            <a v-if="pagesMode && state.card.source_url" :href="state.card.source_url" target="_blank" rel="noopener noreferrer">Page source publiée</a>
            <p v-if="pagesMode">Les textes déjà publiés v4.6.1 sont inchangés. Le mode d'exécution non publié reste inconnu : les étapes 5 et 6 ont une présentation neutre. Votre contexte reste distinct du cas, modifiable et absent du lien. L'accord RAG n'autorise aucun nouvel envoi depuis le parcours. Copier ajoute le contexte et les règles seulement sur clic.</p>
          </details>
        </section>
        <p v-if="publicMode && phase === 'results'" class="secondary-note">Ces résultats sont ceux du RAG actuellement déployé, sans reformulation cachée. Une absence de résultat peut être une limite de ce moteur. Aucune recherche d'orientation transversale n'est disponible ici ; vous pouvez corriger vos choix explicitement.</p>
        <button v-if="state?.allowed_actions.includes('reject')" class="quiet" :disabled="busy" @click="submit({ action: 'reject' })">Aucun de ces cas ne convient</button>
        <nav v-if="state" class="corrections" aria-label="Corriger les choix">
          <button v-for="target in state.back_targets" :key="target" :disabled="busy" @click="submit({ action: 'back', target })">← {{ labels[target] }}</button>
          <button :disabled="busy" @click="submit({ action: 'reset' })">Recommencer</button>
        </nav>
      </article>
    </section>
    <p v-if="externalMode" class="privacy">Une recherche peut prendre des dizaines de secondes, parfois plusieurs minutes selon les quotas Azure. L'hébergement de test ne supprime pas cette attente. Aucune télémétrie sur cette page ; aucun contexte dans les liens.</p>
    <details class="diagnostics">
      <summary>Diagnostic de test — état, filtres, candidats et source</summary>
      <label v-if="!CLOUD_PREVIEW" class="operator-source">Source de la session (opérateur local)
        <select v-model="selectedMode" :disabled="busy" @change="changeSource">
          <option value="PUBLIC_PAGES">PUBLIC_PAGES / RAG sur les pages publiques</option>
          <option value="PUBLIC_API">PUBLIC_API / RAG déjà déployé (non corrigé)</option>
          <option value="SYNTHETIC">SYNTHETIC / fixtures sans modèle</option>
        </select>
      </label>
      <p v-if="publicMode">Le RAG existant n'est pas corrigé par cette connexion. Orientation transversale indisponible ; couverture des 1 021 cas non vérifiée.</p>
      <p v-else-if="source && !pagesMode">Cas fictifs sans modèle ni envoi à un service tiers.</p>
      <p>{{ state?.diagnostics.source.coverage }} {{ state?.diagnostics.source.retrieval_engine }} {{ state?.diagnostics.source.orientation_coverage }}</p>
      <pre>{{ diagnostics }}</pre>
      <a v-if="state?.card" :href="`${PREVIEW_ORIGIN}${state.card.handoff_url}`" target="_blank" rel="noopener noreferrer">Transfert technique et contexte local (JSON)</a>
    </details>
  </main>
</template>

<style scoped>
.preview {
  color-scheme: light;
  --cp-bg: #fafbfc;
  --cp-bg-elevated: #f4f6f8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #eef1f5;
  --cp-border: #d0d7de;
  --cp-border-strong: #8b949e;
  --cp-text: #1f2937;
  --cp-text-muted: #576577;
  --cp-accent: #0969da;
  --cp-accent-hover: #0550ae;
  --cp-accent-soft: rgba(9, 105, 218, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-danger: #b42318;
  --cp-link: #0969da;
}
@media (prefers-color-scheme: dark) {
 .preview {
  color-scheme: dark;
  --cp-bg: #0d1117;
  --cp-bg-elevated: #161b22;
  --cp-surface: #161b22;
  --cp-surface-soft: #21262d;
  --cp-border: #303b4c;
  --cp-border-strong: #6e7c90;
  --cp-text: #f0f6fc;
  --cp-text-muted: #acb8ca;
  --cp-accent: #79b8ff;
  --cp-accent-hover: #a5d0ff;
  --cp-accent-soft: rgba(121, 184, 255, 0.1);
  --cp-accent-fg: #0d1117;
  --cp-danger: #ff958d;
  --cp-link: #79b8ff;
 }
}
.preview { color:var(--cp-text); background:var(--cp-bg); min-height:100vh; padding:24px max(20px,calc((100vw - 980px)/2)); font-family:'Outfit',-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
header { display:flex; align-items:center; justify-content:space-between; gap:16px; padding-bottom:24px; border-bottom:1px solid var(--cp-border); }
a { color:var(--cp-link); }
.brand { color:var(--cp-text); text-decoration:none; font-size:30px; font-weight:800; letter-spacing:-1px; }
.brand span { color:var(--cp-accent); font-weight:800; }
.brand small { display:block; font-size:11px; letter-spacing:.18em; color:var(--cp-text-muted); }
.stable-link { font-size:13px; }
.test-banner { font-size:13px; margin-top:20px; padding:10px 14px; background:var(--cp-accent-soft); border-left:3px solid var(--cp-accent); border-radius:4px; }
.test-banner strong { font-weight:700; margin-right:8px; }
.intro { padding:26px 0 24px; }
.eyebrow { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.13em; color:var(--cp-text-muted); }
h1 { font-size:clamp(24px,3.1vw,34px); line-height:1.25; letter-spacing:-.7px; margin:0 0 10px; font-weight:650; }
.intro>p { color:var(--cp-text-muted); line-height:1.6; }
.source-proof { font-size:12px; margin-top:12px; }
.source-proof span { display:inline-block; }
.workspace { border:1px solid var(--cp-border); border-radius:16px; background:var(--cp-surface); box-shadow:0 4px 14px rgba(13,17,23,.04); }
.case-card { padding:0; }
.selections { display:flex; flex-wrap:wrap; gap:8px; margin-top:16px; }
.selections button { padding:5px 9px; font-size:12px; text-align:left; background:var(--cp-accent-soft); border-color:transparent; }
.selections strong { font-weight:600; }
.selections button:disabled { opacity:1; cursor:default; }
.privacy { font-size:12px; color:var(--cp-text-muted); line-height:1.7; margin-top:18px; }
article { padding:30px; min-width:0; }
.phase-row { display:flex; align-items:center; justify-content:space-between; font-size:12px; color:var(--cp-text-muted); }
.phase { padding:4px 12px; border-radius:.625rem; background:var(--cp-accent-soft); color:var(--cp-accent); font-weight:650; }
h2 { font-size:24px; letter-spacing:-.5px; margin:20px 0 24px; line-height:1.3; }
h3 { font-size:21px; line-height:1.4; margin:10px 0; }
.options { display:grid; gap:10px; }
.domains { grid-template-columns:repeat(2,minmax(0,1fr)); }
button, .link { font:inherit; font-size:13px; cursor:pointer; border-radius:.625rem; }
button { color:var(--cp-text); background:var(--cp-surface); border:1px solid var(--cp-border); padding:8px 12px; }
button:disabled { opacity:.5; cursor:not-allowed; }
button:focus-visible,a:focus-visible,summary:focus-visible,textarea:focus-visible,input:focus-visible { outline:3px solid var(--cp-accent); outline-offset:3px; }
.option { display:flex; align-items:center; justify-content:space-between; gap:12px; text-align:left; color:var(--cp-text); background:var(--cp-surface); border:1px solid var(--cp-border); padding:10px 14px; min-height:48px; line-height:1.45; }
.option:hover:not(:disabled) { border-color:var(--cp-accent); background:var(--cp-accent-soft); }
.option>span { color:var(--cp-accent); }
.problem-label { display:block; font-size:13px; line-height:1.6; margin-bottom:20px; }
.problem-label>span { color:var(--cp-text-muted); }
textarea,input { display:block; box-sizing:border-box; width:100%; margin-top:8px; padding:12px; border:1px solid var(--cp-border-strong); border-radius:.625rem; background:var(--cp-bg-elevated); color:var(--cp-text); font:inherit; }
textarea { resize:vertical; }
.consent { display:flex; align-items:flex-start; gap:10px; margin:16px 0; font-size:14px; }
.consent input { width:18px; height:18px; margin:3px 0 0; accent-color:var(--cp-accent); flex-shrink:0; }
.optional-need { margin-top:16px; font-size:13px; color:var(--cp-text-muted); }
.operator-source { display:block; margin:12px 0; }
.operator-source select { display:block; width:100%; font:inherit; padding:8px; color:var(--cp-text); background:var(--cp-surface); border:1px solid var(--cp-border); }
.choice-input { margin-top:16px; font-size:12px; color:var(--cp-text-muted); }
.choice-input>div { display:flex; align-items:center; gap:8px; margin-top:8px; }
.choice-input input { margin:0; min-width:0; padding:8px 12px; }
.primary { background:var(--cp-accent); color:var(--cp-accent-fg); border:1px solid var(--cp-accent); padding:12px 16px; font-weight:600; }
.primary:hover { background:var(--cp-accent-hover); }
.link { display:inline-block; text-decoration:none; }
.quiet { background:none; color:var(--cp-text); border:0; text-decoration:underline; text-underline-offset:4px; margin:24px 0 4px; padding:4px 0; text-align:left; }
.corrections { display:flex; flex-wrap:wrap; gap:8px 16px; margin-top:32px; padding-top:20px; border-top:1px solid var(--cp-border); }
.corrections button { padding:4px 0; border:0; background:none; color:var(--cp-text-muted); font-size:11px; }
.offer { padding:20px; border:1px solid var(--cp-border); border-radius:16px; margin:16px 0; background:var(--cp-bg-elevated); }
.offer p,.case-card>p { font-size:14px; line-height:1.7; margin-bottom:18px; }
.secondary-note { color:var(--cp-text-muted); font-size:13px; line-height:1.7; }
.error { padding:12px; background:var(--cp-surface-soft); color:var(--cp-text); border:1px solid var(--cp-danger); margin-bottom:20px; border-radius:.625rem; font-size:13px; }
.error button { margin:10px 10px 0 0; }
.diagnostics { margin:24px 0; font-size:12px; color:var(--cp-text-muted); }
summary { cursor:pointer; padding:10px 0; }
.diagnostics pre { background:var(--cp-surface-soft); padding:20px; border-radius:.625rem; white-space:pre-wrap; overflow-wrap:anywhere; font:11px/1.6 Consolas,"Courier New",Courier,monospace; }
.source-details { margin-top:24px; font-size:12px; }
.hash { overflow-wrap:anywhere; }
@media(max-width:760px) { .preview { padding:16px; } header { align-items:flex-start; } .brand { font-size:25px; } .stable-link { max-width:125px; text-align:right; font-size:12px; } .intro { padding:24px 0; } article { padding:24px 16px; } .domains { grid-template-columns:1fr; } .phase-row { gap:12px; } }
</style>
