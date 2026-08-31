#!/usr/bin/env node
/**
 * Smoke test post-déploiement Avoulia (Axe 4.2).
 *
 * Objectif : après chaque déploiement, vérifier en quelques secondes que le contrat
 * critique dont dépend l'expérience (et le bouton parcours) est respecté — SANS aucune
 * dépendance externe (fetch natif de Node 20+). Simple à lancer pour Simplon (C1).
 *
 * Usage :
 *   node smoke-test.mjs                # teste le backend prod par défaut
 *   node smoke-test.mjs https://mon-backend.example.com
 *   SMOKE_BASE_URL=https://... node smoke-test.mjs
 *
 * Code de sortie 0 = tous les tests passent, 1 = au moins un échec.
 *
 * Ce que ça couvre (cf. CHANGELOG.md, bugs B4/B5/B6/B10) :
 *   1. /health répond 200.
 *   2. L'endpoint welcome renvoie un message.
 *   3. Sélection d'un cas → le payload SSE `done` contient un `parcours_url` top-level,
 *      la réponse ne plante pas (pas d'erreur ChatMessage), le pitch n'apparaît qu'UNE fois.
 *   4. La page parcours pointée répond 200.
 *   5. Une réponse de type QUESTION (aucun cas sélectionné) ne renvoie PAS de parcours_url
 *      (garde-fou : le bouton ne doit jamais apparaître trop tôt).
 */

const DEFAULT_BASE = 'https://avoulia-backend.purpleocean-980317d1.francecentral.azurecontainerapps.io';
const BASE = (
  process.argv[2] ||
  process.env.SMOKE_BASE_URL ||
  process.env.PARCOURS_BASE_URL ||
  DEFAULT_BASE
).replace(/\/+$/, '');
const API = `${BASE}/api/v1`;

let passed = 0;
let failed = 0;

function ok(name) {
  passed++;
  console.log(`  \u2713 ${name}`);
}
function ko(name, detail) {
  failed++;
  console.error(`  \u2717 ${name}${detail ? ` — ${detail}` : ''}`);
}

/** Extrait le dernier objet JSON du flux SSE dont une des clés matche `predicate`. */
function parseSseObjects(text) {
  const objects = [];
  for (const line of text.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('data:')) continue;
    const raw = trimmed.slice(5).trim();
    if (!raw) continue;
    try {
      objects.push(JSON.parse(raw));
    } catch {
      /* ligne partielle : ignorée */
    }
  }
  return objects;
}

function countPitch(text) {
  return (text.match(/Passez à l'action/g) || []).length;
}

async function postStream(body) {
  const res = await fetch(`${API}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  return { status: res.status, text, objects: parseSseObjects(text) };
}

async function run() {
  console.log(`\nSmoke test Avoulia — cible : ${BASE}\n`);

  // 1) /health
  try {
    const res = await fetch(`${BASE}/health`);
    const json = await res.json().catch(() => ({}));
    if (res.status === 200 && json.status === 'ok') ok('health = 200 {status:ok}');
    else ko('health', `status=${res.status} body=${JSON.stringify(json)}`);
  } catch (e) {
    ko('health', e.message);
  }

  // 2) welcome
  try {
    const res = await fetch(`${API}/chat/welcome`);
    const json = await res.json().catch(() => ({}));
    if (res.status === 200 && typeof json.message === 'string' && json.message.length > 10) {
      ok('welcome renvoie un message');
    } else {
      ko('welcome', `status=${res.status} body=${JSON.stringify(json)}`);
    }
  } catch (e) {
    ko('welcome', e.message);
  }

  // 3) Sélection d'un cas → parcours_url présent, pas de crash, pitch unique
  let actionUrl = null;
  try {
    const { text, objects } = await postStream({
      message: '1',
      history: [{ role: 'assistant', content: '1. Créer des infographies\n2. Automatiser vos campagnes e-mail marketing' }],
      last_suggested_cases: [
        { id: 'UC-0154', content: 'Créer des infographies et affiches commerciales percutantes' },
        { id: 'UC-0173', content: 'Automatiser vos campagnes e-mail marketing' },
      ],
    });
    const done = objects.find((o) => o.done === true) || {};
    const answer = objects.map((o) => o.t || '').join('');

    if (/ChatMessage/.test(text)) ko('sélection : pas d\'erreur ChatMessage', 'erreur ChatMessage présente');
    else ok('sélection : pas d\'erreur ChatMessage');

    if (typeof done.parcours_url === 'string' && /^https?:\/\/.+action-.+\.html$/.test(done.parcours_url)) {
      ok('sélection : parcours_url top-level présent');
      actionUrl = done.parcours_url;
    } else {
      ko('sélection : parcours_url top-level', `reçu=${JSON.stringify(done.parcours_url)}`);
    }

    const n = countPitch(answer);
    if (n === 1) ok('sélection : pitch affiché exactement une fois');
    else ko('sélection : pitch unique', `${n} occurrence(s)`);
  } catch (e) {
    ko('sélection d\'un cas', e.message);
  }

  // 4) La page parcours répond 200
  if (actionUrl) {
    try {
      const res = await fetch(actionUrl);
      if (res.status === 200) ok('page parcours = 200');
      else ko('page parcours', `status=${res.status}`);
    } catch (e) {
      ko('page parcours', e.message);
    }
  } else {
    ko('page parcours', 'aucune URL de parcours à tester (test 3 échoué)');
  }

  // 5) Garde-fou timing : une QUESTION ne doit pas renvoyer de parcours_url
  try {
    const { objects } = await postStream({
      message: '5',
      history: [{ role: 'assistant', content: 'Dans quel domaine souhaitez-vous agir en priorité ? 1. ... 5. Marketing & visibilité' }],
      // Pas de last_suggested_cases : on est encore dans les questions, aucun cas sélectionné.
    });
    const done = objects.find((o) => o.done === true) || {};
    if (!done.parcours_url) ok('garde-fou timing : pas de parcours_url sur une question');
    else ko('garde-fou timing', `parcours_url inattendu=${done.parcours_url}`);
  } catch (e) {
    ko('garde-fou timing', e.message);
  }

  console.log(`\nRésultat : ${passed} réussi(s), ${failed} échec(s).\n`);
  process.exit(failed === 0 ? 0 : 1);
}

run().catch((e) => {
  console.error('Erreur inattendue du smoke test :', e);
  process.exit(1);
});
