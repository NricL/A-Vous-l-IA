// Détecteur de composants Vue "morts" (non importés) — zéro dépendance.
//
// Pourquoi : la v2 a perdu du temps sur un bug où le vrai composant de chat était
// `HomeView.vue` alors qu'on éditait `ChatView.vue`, un composant MORT (non importé,
// tree-shaké). Ce garde-fou (Axe 4.3) échoue si un `.vue` de `src/` n'est référencé
// nulle part ailleurs — donc plus jamais d'édition d'un fichier fantôme.
//
// Règle : chaque `src/**/*.vue` doit être référencé (par son nom de base, tel qu'il
// apparaît dans un `import X from '.../X.vue'`) dans AU MOINS un autre fichier source.
// Exceptions : `App.vue` (composant racine monté dans main.ts).
//
// Usage : `node scripts/check-dead-code.mjs` depuis le dossier `frontend/`.

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, extname, basename } from 'node:path'

const SRC = 'src'
const ALLOWLIST = new Set(['App']) // composant racine, référencé dans main.ts

/** Liste récursivement les fichiers de `dir` filtrés par extensions. */
function walk(dir, exts) {
  const out = []
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry)
    if (statSync(full).isDirectory()) out.push(...walk(full, exts))
    else if (exts.includes(extname(full))) out.push(full)
  }
  return out
}

const vueFiles = walk(SRC, ['.vue'])
const sourceFiles = walk(SRC, ['.vue', '.ts', '.js', '.mjs', '.tsx', '.jsx'])

// Contenu de tous les fichiers source, indexé par fichier (pour exclure soi-même).
const contents = new Map(sourceFiles.map((f) => [f, readFileSync(f, 'utf8')]))

const dead = []
for (const vf of vueFiles) {
  const name = basename(vf, '.vue')
  if (ALLOWLIST.has(name)) continue
  // Référencé si un AUTRE fichier mentionne son nom de base (import/usage).
  let referenced = false
  for (const [f, text] of contents) {
    if (f === vf) continue
    if (text.includes(name)) {
      referenced = true
      break
    }
  }
  if (!referenced) dead.push(vf)
}

if (dead.length) {
  console.error('\n[X] Composant(s) Vue mort(s) detecte(s) — non importes dans src/ :')
  for (const d of dead) console.error(`   - ${d}`)
  console.error(
    '\nSupprimez-les, ou importez-les la ou ils doivent etre utilises. ' +
      '(Voir HANDOFF.md : bug du composant fantome ChatView.vue.)\n',
  )
  process.exit(1)
}

console.log(`[OK] Aucun composant Vue mort. ${vueFiles.length} composant(s) verifie(s).`)
