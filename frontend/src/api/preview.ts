import { previewOrigin } from '../previewEnvironment'
export { previewOrigin } from '../previewEnvironment'

export type Phase = 'domain' | 'sector' | 'objective' | 'problem' | 'results' | 'orientation' | 'terminal'
export type ActionKind = 'choose' | 'describe' | 'back' | 'reset' | 'reject' | 'accept' | 'refuse'
export interface PreviewOption {
  id: string
  label: string
  number: number
  case_id?: string
  domain_label?: string
  objective_label?: string
  sector?: string | null
  source_sectors?: string[]
  sector_revalidation_required?: boolean
}
export interface PreviewState {
  protocol_version: 1
  session_id: string
  revision: number
  catalogue_revision: string
  phase: Phase
  question: { id: string; phase: Phase; prompt: string; options: PreviewOption[] }
  confirmed: {
    domain: string | null; domain_label: string | null
    sector: string | null; objective: string | null; objective_label: string | null
  }
  initial_need: string
  problem_original: string
  allowed_actions: ActionKind[]
  back_targets: Phase[]
  warning: string
  card: null | {
    case_id: string; title: string; description: string; source_hash: string
    source_url: string | null; parcours_url: string | null; handoff_url: string
    preview_parcours_url: string
    parcours_render_policy: 'public-neutral-v1' | 'published-original' | 'synthetic-source-mode' | 'unavailable'
  }
  diagnostics: {
    main: null | { filters_applied: Record<string, unknown>; candidate_ids: string[]; result_ids: string[]; engine: string; details?: Record<string, unknown> }
    orientation: null | { filters_applied: Record<string, unknown>; candidate_ids: string[]; result_ids: string[]; engine: string; details?: Record<string, unknown> }
    source: PreviewSource
  }
}
export interface PreviewSource {
  source_mode: 'SYNTHETIC' | 'PUBLIC_API' | 'PUBLIC_PAGES'
  catalogue_version: string
  case_count: number
  coverage: string
  retrieval_engine: string
  orientation_coverage: string
  privacy?: string
  source_url?: string
}
export interface PreviewAction {
  action: ActionKind
  choice_id?: string
  choice_text?: string
  target?: Phase
  text?: string
  initial_need?: string
}

export const CLOUD_PREVIEW = import.meta.env.VITE_AVIA_PREVIEW_CLOUD === 'true'
export const PREVIEW_ORIGIN = previewOrigin(import.meta.env.VITE_AVIA_PREVIEW_ORIGIN
  || `http://127.0.0.1:${import.meta.env.VITE_AVIA_PREVIEW_PORT || 8767}`,
  CLOUD_PREVIEW ? import.meta.env.VITE_AVIA_PREVIEW_ORIGIN || 'missing-cloud-origin' : '')
const API = `${PREVIEW_ORIGIN}/api/preview/v1`

function sourceMode(mode?: PreviewSource['source_mode']) {
  if (CLOUD_PREVIEW && mode && mode !== 'PUBLIC_PAGES') {
    throw new Error('Cette version de test utilise uniquement les pages publiques v4.6.1.')
  }
  return CLOUD_PREVIEW ? 'PUBLIC_PAGES' : mode
}

export class PreviewError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message)
  }
}

async function jsonResponse(response: Response): Promise<PreviewState> {
  const payload = await response.json()
  if (!response.ok) {
    throw new PreviewError(response.status, payload.error ?? 'http_error', payload.message ?? 'La requête a échoué.')
  }
  if (payload.protocol_version !== 1 || !payload.question?.id || !Number.isInteger(payload.revision)) {
    throw new PreviewError(409, 'protocol_version', 'Réponse de protocole incompatible.')
  }
  if (CLOUD_PREVIEW) sourceMode(payload.diagnostics?.source?.source_mode ?? 'SYNTHETIC')
  return payload
}

export async function readPreviewSource(signal?: AbortSignal, mode?: PreviewSource['source_mode']): Promise<PreviewSource> {
  mode = sourceMode(mode)
  const response = await fetch(`${PREVIEW_ORIGIN}/health${mode ? `?source_mode=${mode}` : ''}`, {
    signal, cache: 'no-store', referrerPolicy: 'no-referrer', credentials: 'omit', redirect: 'error',
  })
  const payload = await response.json()
  if (!response.ok || !['SYNTHETIC', 'PUBLIC_API', 'PUBLIC_PAGES'].includes(payload.source?.source_mode)) {
    throw new PreviewError(response.status, 'unknown_source', 'Source de préversion indisponible ou inconnue.')
  }
  sourceMode(payload.source.source_mode)
  return payload.source
}

export async function createPreview(signal?: AbortSignal, externalConsent = false, mode?: PreviewSource['source_mode']): Promise<PreviewState> {
  mode = sourceMode(mode)
  if ((CLOUD_PREVIEW || mode === 'PUBLIC_PAGES' || mode === 'PUBLIC_API') && !externalConsent) {
    throw new Error("Confirmez d'abord l'envoi aux modèles Azure pour cette session.")
  }
  return jsonResponse(await fetch(`${API}/sessions`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ protocol_version: 1, external_consent: externalConsent, source_mode: mode }),
    signal, cache: 'no-store', referrerPolicy: 'no-referrer', credentials: 'omit', redirect: 'error',
  }))
}

export async function readPreview(session: string, signal?: AbortSignal): Promise<PreviewState> {
  return jsonResponse(await fetch(`${API}/sessions/${encodeURIComponent(session)}`, {
    signal, cache: 'no-store', referrerPolicy: 'no-referrer', credentials: 'omit', redirect: 'error',
  }))
}

export function actionEnvelope(state: PreviewState, action: PreviewAction, requestId: string) {
  return {
    ...action, protocol_version: 1, session_id: undefined,
    catalogue_revision: state.catalogue_revision, revision: state.revision,
    question_id: state.question.id, request_id: requestId,
  }
}

export async function sendPreviewAction(
  state: PreviewState, action: PreviewAction, requestId: string, signal?: AbortSignal,
): Promise<PreviewState> {
  return jsonResponse(await fetch(`${API}/sessions/${encodeURIComponent(state.session_id)}/actions`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(actionEnvelope(state, action, requestId)),
    signal, cache: 'no-store', referrerPolicy: 'no-referrer', credentials: 'omit', redirect: 'error',
  }))
}

export function acceptsResponse(current: PreviewState | null, next: PreviewState, expectedSession: string): boolean {
  return next.protocol_version === 1 && next.session_id === expectedSession
    && (current === null || current.session_id === next.session_id && next.revision >= current.revision)
}
