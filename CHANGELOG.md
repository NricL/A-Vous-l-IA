# Avoulia — Changelog v1 → v2 (synthèse d'onboarding)

**But de ce document :** permettre à un dev Simplon — **notamment celui qui a participé à la
v1** — de comprendre **en une lecture** tout ce qui a changé entre la v1 publique et la v2
livrée. C'est le point d'entrée « traçabilité » du projet (contrainte C2, cf.
[`README.md`](./README.md)).

- **Détail chronologique fin :** [`SUIVI_PROJET.md`](./SUIVI_PROJET.md)
- **Reprise technique & pièges :** [`HANDOFF.md`](./HANDOFF.md)
- **Évolutions à venir :** [`ROADMAP.md`](./ROADMAP.md)
- **Historique exact :** `git log` (34 commits, `ab4b21a` → `d02ad1d` au 2026-08-26)

> Convention : chaque entrée indique **Quoi / Pourquoi / Où (fichiers)** et le **commit**.

---

## 1. Point de départ — v1 (référence)

- **Commit :** `ab4b21a` — « Public release » (2026-05-19), dépôt d'origine Simplon
  (`github.com/simplonco/avouslia`).
- **Ce qu'est la v1 :** un chatbot RAG open source aidant à explorer des cas d'usage IA.
  - **Backend :** FastAPI + **Haystack** (pipelines RAG) + **Chroma** (store vectoriel),
    LLM OpenAI/Azure.
  - **Frontend :** Vue 3 (Vite).
  - Restitution des fiches de cas depuis une base (Excel) de cas d'usage.

La v2 **ne réécrit pas** la v1 : elle l'étend (parcours guidés, télémétrie, industrialisation)
puis corrige une série de bugs de fond découverts en production.

---

## 2. Ce que la v2 ajoute — vue d'ensemble

1. **Parcours personnalisés** : après la sélection d'un cas, un **bouton** mène à une page
   « parcours » (6 étapes ~2h, quick win + prompts). ~1025 pages statiques générées.
2. **Parcours conversationnel guidé** : `Q1 domaine → Q1.5 secteur (optionnel) → Q2 objectif
   → Q3 problème → liste de ~5 cas → sélection → fiche détail + bouton parcours`.
3. **Télémétrie** (Azure App Insights) : événements du funnel chat → RAG → parcours.
4. **Industrialisation** : IaC (Bicep), config par environnement, requêtes KQL, docs de
   handover.
5. **Fiabilisation** : nombreux correctifs RAG/UX/déploiement (section 4).

### Architecture v2 (déployée)

| Composant | Techno | Hébergement Azure |
|---|---|---|
| Backend | FastAPI + Haystack + Chroma + Azure OpenAI | Container App `avoulia-backend` (`rg-avoulia-fr-dev`) |
| Frontend | Vue 3 (build Vite) servi par nginx | Container App `avoulia-frontend` |
| Pages parcours | HTML statiques (`action-<hash>.html`) | servies par le backend |
| Registry images | — | `acravoulia97186.azurecr.io` |
| Télémétrie | App Insights + Log Analytics + Workbook | — |

**Contraintes non-négociables (héritées, toujours valables) :**
- Restitution **verbatim** des champs de la base (pas de reformulation LLM à l'affichage).
- **Pré-filtrage par métadonnées** (domaine/secteur/intention) **avant** la recherche vectorielle.
- Base Excel **jamais exposée** publiquement.
- **`AVOULIA_SALT` fixe en prod** : le changer casse tous les liens parcours (cascade de 404).
- Pages parcours **non indexées** (`noindex`).

---

## 3. Évolutions fonctionnelles v2 (par thème)

### 3.1 Parcours : génération, routage, liens
- **Quoi :** génération des pages parcours, puis simplification du routage vers des pages
  **statiques** servies par le backend ; liens parcours **toujours** présents dans une fiche
  détail ; mapping `UC-xxxx → hash` via CSV local (fallback hash déterministe).
- **Pourquoi :** fiabiliser l'ouverture des pages (éviter les 404) et garder un déploiement simple.
- **Où :** `backend/app/parcours_util.py`, `backend/app/static/parcours/…`,
  `backend/scripts/generate_parcours_pages.py`, `avoulia-parcours/` (générateur public).
- **Commits :** `0f4588c`, `cdf885c`, `a491eec`, `0d8ebaa`, `9237492`, `6b83542`, `fe6a9f1`,
  `6249fb1`, `34af4ee` (2026-07).

### 3.2 Télémétrie & industrialisation
- **Quoi :** App Insights (8 événements funnel), config par environnement, Bicep IaC,
  requêtes KQL, Workbook, guide de handover.
- **Pourquoi :** mesurer l'usage et rendre la reprise/déploiement simples pour Simplon (C1).
- **Où :** `frontend/src/appinsights.ts`, `infra/` (Bicep, KQL, dashboards),
  `config/environments/…`, `HANDOFF.md`.
- **Commits :** `5929370`, `0f4588c`, `f0abacc` (2026-07).

### 3.3 Qualité du parcours guidé (Q1→Q3) & sélection de cas
- **Quoi :** meilleur classement de certains cas ; clarification que « Autre / Non spécifique »
  est ajouté automatiquement aux secteurs ; cohérence entre cas **affichés** et cas
  **sélectionnables**.
- **Pourquoi :** éviter les incohérences de sélection (« je ne peux détailler que 1 à 3 »).
- **Où :** `backend/app/haystack_rag.py`, `backend/app/rag_constants.py`.
- **Commits :** `753b3ba`, `1b702fa`, `cb8179b`.

### 3.4 Réponse terminale après choix d'un cas
- **Quoi :** après sélection d'un cas, le bot donne les **infos utiles** puis **propose le
  parcours** — sans reposer de question ni offrir de faux choix (« détail complet / plan
  synthétique », « Répondez 1 ou 2 »).
- **Pourquoi :** comportement attendu = terminal, orienté action.
- **Où :** `backend/app/haystack_rag.py` (prompt + nettoyage), `backend/app/routes/chat.py`.
- **Commits :** `d4104a5`, `fd77fff`.

### 3.5 Bouton parcours cliquable & pitch industrialisé
- **Quoi :** le lien parcours n'est plus du texte brut à copier — c'est un **bouton
  cliquable**. Le texte du pitch et le libellé du bouton viennent d'une **source unique**
  (`get_parcours_pitch()`), dérivée de la structure réelle du parcours (6 étapes, ~2h).
- **Pourquoi :** donner envie de cliquer + éviter la désynchronisation texte/bouton.
- **Où :** `backend/app/parcours_util.py`, `backend/app/routes/chat.py`,
  `backend/app/models.py`, `frontend/src/views/HomeView.vue`.
- **Commits :** `955b574`, `3bd7d85`, `6a6a7fa`, `eb198c1`.

### 3.6 UX guidée v2 (chips, stepper, retour arrière) & carte cas verbatim
- **Quoi :** message d'accueil non répété ; **chips cliquables** à chaque étape (Q1/secteur/objectif,
  puis « Cas 1…5 ») ; **stepper de progression** 6 étapes (Domaine → Secteur → Objectif →
  Problème → Cas d'usage → Parcours) avec **retour arrière** cliquable ; carte de cas
  **100 % verbatim** de la base (titre, badges effort/mode/données, description, déclencheurs) —
  **plus aucun texte de pertinence généré par le LLM** (règle D1).
- **Pourquoi :** parcours plus lisible et « cliquable » ; conformité stricte à la restitution
  verbatim ; mobile-friendly (cibles tactiles ≥ 40 px).
- **Où :** `frontend/src/views/HomeView.vue` (LE composant chat), `backend/app/haystack_rag.py`
  (`build_niveau2_block`), `backend/app/routes/chat.py`, `frontend/nginx.conf`, `smoke-test.mjs`.

### 3.7 Statistiques d'usage intégrées (Axe 3.1) — page `/stats`
- **Quoi :** suivi **simple et intégré** (aucune infra ni dashboard externe) des éléments les
  plus visités — **domaines (rôles)**, **problématiques (Q3)**, **cas d'usage consultés** — plus
  les **clics sur le bouton parcours** (conversion clé). Consultable sur la page `/stats` servie
  par le backend ; endpoint JSON `/api/v1/stats.json`.
- **Pourquoi :** répondre au besoin « savoir ce qui est le plus visité » **sans** ajouter de
  repo/produit/complexité pour Simplon (C1). Compatible avec le futur mono-conteneur.
- **Comment :** un module `stats.py` écrit un **append blob** Azure (`STORAGE_ACCOUNT_NAME/KEY`),
  avec **repli en mémoire** si le stockage n'est pas configuré. Enregistrement branché dans le
  flux chat (domaine à sa sélection, problème sur texte libre Q3, cas à l'ouverture de la carte)
  et un endpoint `POST /api/v1/chat/parcours-click` appelé par le frontend au clic du bouton.
- **Où :** `backend/app/stats.py` (nouveau), `backend/app/main.py` (routes `/stats`,
  `/api/v1/stats.json`), `backend/app/routes/chat.py` (`_record_usage_stats`, `parcours-click`),
  `backend/app/haystack_rag.py` (`stats.record("cas", …)`), `frontend/src/api/chat.ts`
  (`trackParcoursClick`), `frontend/src/views/HomeView.vue` (`onParcoursClick`).
- **Validé :** E2E navigateur (domaine → secteur → objectif → problème → cas → clic parcours),
  `/stats` affiche les 4 types ; storage branché sur `stavoulia97186` (durabilité).

---

## 4. Bugs de fond corrigés — « pièges à connaître » ⚠️

Ces bugs ont été coûteux à diagnostiquer : un dev qui reprend le code **doit** les connaître.

| # | Symptôme | Cause racine | Correctif | Commit |
|---|---|---|---|---|
| B1 | Cas d'une **autre intention** dans la liste ; moins de cas sélectionnables qu'affichés | « Fallbacks silencieux » retombant sur **tous les docs du domaine** ; prompt imposant « min 3 cas » → le LLM inventait des cas | Supprimer les fallbacks élargissants ; ne jamais lâcher l'intention ; règle anti-hallucination | `2aafe0f` |
| B2 | `'ChatRequest' object has no attribute 'pending_case_index'` | Référence à un champ inexistant du modèle | Suppression de la référence | `953455a` |
| B3 | Bouton parcours qui ne s'affichait pas (contexte cas perdu en SSE) | Le contexte du cas n'était pas conservé côté flux | Conserver le contexte cas + payload backend | `b2d872e`, `f497a02` |
| B4 | `cannot import name 'AzureOpenAIGenerator'` (crash à la sélection) | API Haystack : les générateurs **texte** ont disparu | Migrer vers `AzureOpenAIChatGenerator`/`OpenAIChatGenerator`, `ChatPromptBuilder`, `ChatMessage` | `816c1e5` |
| B5 | `'ChatMessage' object has no attribute 'strip'` | L'API chat renvoie un `ChatMessage` (texte via **`.text`**, plus `.content`) | Helper unique `_reply_to_text()` | `3bd7d85` |
| B6 | Bloc « 🚀 Passez à l'action » **dupliqué** | Pitch ajouté à deux endroits, dédup uniquement si URL brute présente | Sentinelle `PARCOURS_PITCH_SENTINEL` + ajout **idempotent** | `fb2e773` |
| B7 | Un correctif présent dans le `.py` déployé **sans effet** en prod | **Bytecode `.pyc` périmé** embarqué dans l'image et exécuté à la place de la source | Dockerfile purge `__pycache__` + `PYTHONDONTWRITEBYTECODE=1` | `fb2e773` |
| B8 | Le bouton n'apparaissait jamais dans l'UI | Le code du bouton était dans **`ChatView.vue`… jamais importé** (mort) ; le vrai composant est **`HomeView.vue`** | Implémenter le bouton dans `HomeView.vue` ; supprimer `ChatView.vue` | `6a6a7fa` |
| B9 | Déploiement non pris en compte (ancien JS chargé) | `index.html` mis en cache par le navigateur | nginx : `index.html` en `no-cache`, assets hashés `immutable` | `6a6a7fa` |
| B10 | Bouton affiché **trop tôt** (pendant Q1.5/Q2/Q3) | Fallback frontend devinant un cas dès qu'on tapait un chiffre | Bouton piloté **uniquement** par `payload.parcours_url` (backend) | `eb198c1` |

**Règle générale tirée de B1/B7/B8/B10 :** privilégier une **source de vérité unique et
autoritaire** (backend) plutôt que des fallbacks/devinettes ; se méfier des artefacts
périmés (`.pyc`, cache, code mort).

---

## 5. Carte de la documentation (où trouver quoi)

| Besoin | Document |
|---|---|
| Principe projet (livraison Simplon, traçabilité) | [`README.md`](./README.md) (en-tête) |
| Vue d'ensemble v1 → v2 (ce fichier) | `CHANGELOG.md` |
| Détail chronologique de chaque correctif/déploiement | [`SUIVI_PROJET.md`](./SUIVI_PROJET.md) |
| Reprise technique, pièges, API Haystack, CTA autoritaire, cache, bytecode | [`HANDOFF.md`](./HANDOFF.md) |
| Évolutions prévues & priorités | [`ROADMAP.md`](./ROADMAP.md) |
| Installation & lancement local | [`README.md`](./README.md), [`frontend/README.md`](./frontend/README.md) |

---

## 6. Comment vérifier une reprise (checklist express)

1. **Lancer local** (cf. README) → chat accessible, `/health` = 200.
2. **Rejouer le parcours** : domaine → secteur → objectif → problème → liste → sélectionner un cas.
3. **Vérifier le bouton parcours** : il n'apparaît **qu'après** sélection d'un cas, une seule
   fois, et ouvre une page `action-<hash>.html` (HTTP 200).
4. **Tests backend** : `python -m unittest discover -s tests` (doit être vert).
5. **Smoke test post-déploiement** : `node smoke-test.mjs [url-backend]` — script sans dépendance
   qui vérifie en quelques secondes le contrat critique (health, welcome, sélection → parcours_url,
   page 200, garde-fou timing). À lancer après **chaque** déploiement.
6. En cas de « le fix ne prend pas en prod » : penser **bytecode `.pyc`** (B7) et **cache
   navigateur** (B9) avant tout.
