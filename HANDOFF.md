# Avoulia V2 — Implementation Handover Guide for Simplon

**Status:** Ready for Handover (2026-07-10)  
**Target:** Deploy Avoulia V2 with Parcours Pages + App Insights Telemetry to Production Azure  
**Audience:** Simplon DevOps / Backend Team

> **Documents de référence (onboarding v1 → v2) :**
> [`CHANGELOG.md`](./CHANGELOG.md) (**synthèse v1 → v2 — commencer ici**) ·
> [`ROADMAP.md`](./ROADMAP.md) (évolutions prévues & priorités) ·
> [`SUIVI_PROJET.md`](./SUIVI_PROJET.md) (journal chronologique des correctifs) ·
> [`README.md`](./README.md) (install & lancement local). Un dev Simplon ayant fait la v1
> doit lire ces fichiers + ce guide pour comprendre tout ce qui a changé depuis la v1.

---

## 📋 Overview

Avoulia V2 adds **parcours pages** (guided implementation steps) + **real-time telemetry** to the existing RAG chatbot system. When a PME asks a question:

1. **Backend** returns RAG response + **parcours URL** (`/action/<hash>/`)
2. **Frontend** displays URL to PME
3. **PME clicks** → Opens parcours page (tracks: validation, 6 steps, quickwin)
4. **App Insights** records full funnel: chat → RAG → parcours → step completion
5. **Dashboard (Workbook)** shows: funnel %, top cases, retention, bounce rate

---

## 🚀 Implementation Steps (Production Ready)

### Phase 1: Azure Infrastructure (Bicep)

**Files to use:**
- `infra/main.bicep` — IaC template (App Insights, Log Analytics, Storage)
- `config/environments/prod.officiel.sample.json` — Production parameters template

**Steps:**

1. **Prepare environment config:**
   ```bash
   # Copy template and fill production values
   cp config/environments/prod.officiel.sample.json config/environments/prod.officiel.json
   
   # Edit prod.officiel.json:
   # - resourceGroup: rg-avoulia-fr-prod
   # - region: westeurope
   # - subscription: <your-prod-subscription-id>
   # - appInsights name: ai-avoulia-prod
   # - storage account: stavouliafr4prod (must be globally unique)
   ```

2. **Deploy Bicep to Production:**
   ```bash
   az group create \
     --name rg-avoulia-fr-prod \
     --location westeurope
   
   az deployment group create \
     --resource-group rg-avoulia-fr-prod \
     --template-file infra/main.bicep \
     --parameters @config/environments/prod.officiel.json
   ```

3. **Capture Outputs:**
   After deployment succeeds, capture these values (you'll need them):
   ```bash
   az deployment group show \
     --resource-group rg-avoulia-fr-prod \
     --name main \
     --query "properties.outputs" > outputs.json
   
   # Extract and store in GitHub Secrets:
   # - APPINSIGHTS_INSTRUMENTATION_KEY_PROD (from outputs.appInsightsKey)
   # - APPINSIGHTS_CONNECTION_STRING_PROD (from outputs.appInsightsConnectionString)
   # - STORAGE_ACCOUNT_NAME_PROD (from outputs.storageAccountName)
   # - STORAGE_ACCOUNT_KEY_PROD (from outputs.storageAccountKey)
   ```

---

### Phase 2: Backend Enhancement (Chantier E)

**File to modify:**
- `backend/app/routes/chat.py` (or your main chat endpoint)

**Changes:**

1. **Add parcours URL generation to chat endpoint:**
   - Reference: `backend/CHANTIER_E_BACKEND_ENDPOINT.py` (template provided)
   - Implement `generate_case_hash(case_id, salt)` function
   - Update chat response to include:
     ```python
     {
       "answer": "...",  # RAG response (Q2 + Q3 text)
       "case_id": "UC-0042",
       "case_hash": "vn38reuyw7",
       "parcours_url": "https://avoulia.azurewebsites.net/action/vn38reuyw7/",
       "matching_score": 0.92,
       ...
     }
     ```

2. **Environment variables (set in Container Apps):**
   ```
   AVOULIA_SALT = "prod-salt-value-NEVER-rotate-in-prod"
   PARCOURS_BASE_URL = "https://avoulia.azurewebsites.net"
   APPINSIGHTS_INSTRUMENTATION_KEY = <from Bicep outputs>
   ```

3. **Test locally:**
   ```bash
   export AVOULIA_SALT="test-salt-123"
   export PARCOURS_BASE_URL="http://localhost:5173"
   python -m pytest tests/test_chat_endpoint.py -v
   ```

---

### Phase 3: Frontend Integration (Chantier C)

**Files to modify:**
- `frontend/src/main.ts` — Initialize App Insights on load
- `frontend/index.html` — Add telemetry snippet to `<head>`
- `frontend/src/components/ChatMessage.vue` — Track user messages + RAG hits
- `frontend/src/components/ParcoursPage.vue` — Track step completion (if exists)

**Changes:**

1. **Add App Insights snippet:**
   Reference: `frontend/src/appinsights-instrumentation.html`
   
   Copy the script into `frontend/src/appinsights.ts`:
   ```typescript
   // frontend/src/appinsights.ts
   
   export const appInsights = {
     sessionId: getSessionId(),
     
     trackChatSessionStart: () => { /* ... */ },
     trackUserMessage: (msg) => { /* ... */ },
     trackRagResult: (caseId, score) => { /* ... */ },
     trackParcoursUrlProposed: (url) => { /* ... */ },
     // ... other methods
   };
   ```

2. **Track user message in chat component:**
   ```vue
   <!-- frontend/src/components/ChatMessage.vue -->
   <script setup>
   import { appInsights } from '@/appinsights';
   
   const sendMessage = async () => {
     appInsights.trackUserMessage(messageText, 'pme_question');
     const response = await fetchFromBackend(messageText);
     appInsights.trackRagResult(response.case_id, response.matching_score);
     if (response.parcours_url) {
       appInsights.trackParcoursUrlProposed(response.parcours_url, response.case_hash);
     }
   }
   </script>
   ```

3. **Environment variables (build time):**
   Set `VITE_APPINSIGHTS_KEY` in GitHub Secrets → injected by CI/CD

---

### Phase 4: Parcours Pages (Chantier B — Reference)

**Reference files:**
- `templates/page.html.j2` — Jinja2 template for parcours pages
- `frontend/src/appinsights-instrumentation.html` — Telemetry integration

**Architecture:**
- Pages can be **static** (pre-generated) or **dynamic** (server-rendered)
- Each page has a unique `<body data-case-hash="UC-0042">` attribute
- Telemetry auto-tracks step completion when checkboxes are marked

**Quick checklist:**
- [ ] Étape 1 (validation) at top (appears expanded by default)
- [ ] Transition message "✓ OK, c'est pour vous" visible
- [ ] Étapes 2-6 collapsed below
- [ ] Quick win accordion at bottom (closed by default)
- [ ] App Insights events fire on step/quickwin interactions

---

### Phase 5: Dashboard & Monitoring (Chantier D)

**Files:**
- `infra/kql-queries.kql` — Pre-written KQL queries
- `infra/dashboards/avoulia-parcours-dashboard.json` — Workbook JSON

**Setup:**

1. **Import Workbook to Azure Portal:**
   ```bash
   az monitor workbooks create \
     --resource-group rg-avoulia-fr-prod \
     --definition @infra/dashboards/avoulia-parcours-dashboard.json \
     --name avoulia-parcours-dashboard
   ```

2. **Verify KQL Queries Work:**
   - Go to: Azure Monitor → Logs
   - Paste each query from `infra/kql-queries.kql`
   - Verify data flows (after 5-10 min of traffic)

3. **Dashboard Metrics Tracked:**
   - **Funnel:** chat_start → RAG_hit → parcours_opened → step_completion
   - **Top Cases:** Most-visited parcours pages
   - **Quickwin Rate:** % of users who copied quick solution
   - **Retention:** J+1, J+3, J+7 re-engagement
   - **Bounce Rate:** Chat sessions with no RAG result
   - **Timeline:** Event volume per hour

---

## 🔧 Configuration Reference

### Environment Variables (Prod)

| Variable | Value | Source |
|---|---|---|
| `AVOULIA_SALT` | `prod-salt-...` (fixed) | Set in Container Apps secret |
| `PARCOURS_BASE_URL` | `https://avoulia.azurewebsites.net` | Hardcode in backend config |
| `APPINSIGHTS_INSTRUMENTATION_KEY` | From Bicep output | GitHub Secret → CI/CD |
| `APPINSIGHTS_CONNECTION_STRING` | From Bicep output | For SDK initialization |
| `STORAGE_ACCOUNT_NAME` | `stavouliafr4prod` | From Bicep output |
| `STORAGE_ACCOUNT_KEY` | From Bicep output | For mapping CSV access |

### Storage (Mapping CSV)

The backend can optionally load `mapping_uc_hash.csv` from Blob Storage:
```
Storage Account: stavouliafr4prod
Container: parcours-mappings
File: mapping_uc_hash.csv

Format:
case_id,case_hash
UC-0001,vn38reuyw7
UC-0002,kx92mnopq3
...
```

If not using dynamic mapping, case hashes are generated deterministically via `AVOULIA_SALT`.

---

## ✅ Validation Checklist (Before Go-Live)

### Backend
- [ ] Chat endpoint returns `parcours_url` field
- [ ] `case_hash` is deterministic (same input → same hash)
- [ ] Environment variables are set correctly
- [ ] Local test: `curl http://localhost:8000/api/v1/chat -X POST -d '{"message": "test"}'` returns URL

### Frontend
- [ ] Chat page loads without errors
- [ ] Telemetry events appear in browser DevTools → Network → App Insights calls
- [ ] User message + RAG result trigger events
- [ ] Parcours URL is clickable in response

### Parcours Page
- [ ] Page loads (HTTP 200)
- [ ] Headers include `X-Robots-Tag: noindex, nofollow, noarchive` + meta noindex
- [ ] Étape 1 validation appears first
- [ ] Steps track completion (check DevTools Console for event logs)
- [ ] Quickwin accordion is collapsible

### App Insights
- [ ] Bicep deployment succeeded (all resources created)
- [ ] Data flows in: `customEvents` table populated
- [ ] KQL queries return non-zero results
- [ ] Workbook dashboard loads without errors
- [ ] Funnel metrics make sense (each step < previous)

---

## 🩹 Known Issues Fixed (2026-08-25) — Read Before Modifying `haystack_rag.py`

Two related bugs were found and fixed in the RAG retrieval/qualification pipeline (`backend/app/haystack_rag.py`). **Both share the same root cause pattern**, and it's important Simplon's team understands it before touching this file, to avoid reintroducing it.

**Symptoms observed:**
1. When a user selected a specific marketing objective (e.g. "Créer des contenus marketing"), the reformulation examples (Q3) and some suggested cases actually belonged to *other* marketing objectives (acquisition, market analysis, campaigns, etc.) — an intention mismatch.
2. The bot displayed up to 5 numbered use cases, but rejected the user's selection of case 4 or 5 ("Le choix « 4 » n'est pas disponible... 1, 2 ou 3") — meaning fewer real cases were actually retrieved than were shown in the text.

**Root cause (anti-pattern):** several places in the retrieval pipeline had a "graceful fallback" of the form `filtered_docs if filtered_docs else all_domain_docs` (or literally dropping the `intention` filter condition) to avoid returning an empty result when the strict filter (`domaine` + `intention` + `secteur`) matched too few documents. This silently reintroduced off-topic documents from *other* intentions into the pool. Separately, the RAG prompt hard-coded a "minimum 3 cases" instruction with no guarantee that 3 real documents existed, which caused the LLM to invent extra cases to satisfy the minimum — explaining the gap between displayed cases and selectable `suggested_case_ids`.

**Fix applied:**
- `build_pool()`: removed the `docs = filtered if filtered else docs` fallback — now returns an empty list rather than mixing intentions.
- `_retrieve_docs_for_question()`: reordered the fallback cascade so the `intention` filter is **never dropped** (domain+intention+secteur → domain+intention+secteur-élargi → domain+intention only, with sector applied as a Python post-filter).
- `RAG_PROMPT`: replaced "Minimum 3 cas / Maximum 5 cas" with an absolute anti-hallucination rule — never present more cases than actually provided, never pad below 3 with invented ones.
- `_build_rag_prompt_from_docs()`: removed a dead code branch that implied (but never enforced) a minimum-3 display rule.
- Added 3 regression tests in `backend/tests/test_haystack_rag.py` (the file now has 11 tests, all passing).
- Deployed to `avoulia-backend` (revision `avoulia-backend--0000023`) in `rg-avoulia-fr-dev`.

**⚠️ Guidance for future changes:** if you see a similar "no results, so fall back to something broader" pattern anywhere else in `haystack_rag.py`, treat it as a code smell — prefer returning an empty/partial result (and letting the LLM say "no matching case found") over silently mixing categories. See `SUIVI_PROJET.md`, entry "Update 2026-08-25 — Fix filtrage RAG", for full detail.

---

## 🔗 Parcours Link CTA (2026-08-25) — Single Source of Truth for Button/Text Wording

The parcours link is **no longer shown as raw text** requiring copy-paste — the frontend (`ChatView.vue`) renders it as a clickable button (`SuggestedCase.parcours_url`).

The text/label around it (step count, duration, CTA wording) is **not hardcoded in multiple places**. It all comes from one function: `backend/app/parcours_util.get_parcours_pitch()`, driven by two constants:
- `PARCOURS_STEPS_COUNT` (currently 6)
- `PARCOURS_ACTIVE_MINUTES` (currently 132, i.e. sum of the fixed-duration steps in `generate_parcours_pages.py`, excluding the open-ended "test during your week" step)

Both `routes/chat.py` and `haystack_rag.py` call this function for the chat message text, and `models.SuggestedCase.parcours_cta_label` propagates the same computed button label to the frontend — so text and button are always in sync.

**If the parcours page template changes** (more/fewer steps, different durations), update only the two constants in `parcours_util.py`. Do not hardcode new wording anywhere else — that would defeat the purpose of this single source of truth and risks the button/text drifting out of sync again.

---

## 🎯 Parcours CTA — Backend Is Authoritative (2026-08-26)

**Do not let the frontend guess which case was selected.** On any case-detail
response, the backend (`get_rag_prompt_and_sources`) returns the selected case's
`parcours_url` and `parcours_cta_label` as **top-level fields** of the SSE `done`
payload. The frontend (`resolveParcoursCta` in **`HomeView.vue`** — the live chat
component) reads these fields **first**; the old resolution-by-id/index/typed-digit
is only a fallback.

- **Why:** previously the button was reconstructed on the frontend by matching
  `suggested_cases[index]` against the digit the user typed. That was fragile
  (affirmations like "ok", free-text detail requests, uncaught numbers) and often
  produced a missing button even though the message said "click the button below".
- **Backend:** `_ret_niveau2(payload, selected_id=...)` computes the URL/label via
  `build_parcours_info(selected_id)` and appends them to the returned tuple, which
  `routes/chat.py` puts into `done_payload["parcours_url"] / ["parcours_cta_label"]`.
- **Rule for future changes:** the selected-case parcours button must stay
  **backend-driven**. Never reintroduce index-based guessing as the primary path.
  (A digit-based fallback was removed on 2026-08-26 because it made the button
  appear during the Q1.5/Q2/Q3 questions whenever the user answered with a digit.)

## 🧩 Haystack Chat Generator API (2026-08-26)

The installed Haystack exposes **chat** generators only:
`AzureOpenAIChatGenerator` / `OpenAIChatGenerator` (built via
`ChatPromptBuilder` + `ChatMessage`, connected on `generator.messages`). The old
`AzureOpenAIGenerator` / `OpenAIGenerator` (text-completion) no longer exist and
importing them crashes at runtime.

Replies are `ChatMessage` objects whose text is accessed via **`.text`** (not the
old `.content`). Always extract text through the helper `_reply_to_text()` in
`haystack_rag.py` — it handles `.text`, legacy `.content`, and plain strings.
Calling `.strip()` directly on a reply crashes with
`'ChatMessage' object has no attribute 'strip'`.

---

## 📊 Usage Stats — Integrated `/stats` Page (2026-08-27)

Simple, **self-contained** usage tracking — no external product, no separate repo, no dashboard
service (constraint C1). Answers "which roles/problems/cases are most visited?".

- **Where to look:** open **`/stats`** on the backend (e.g.
  `https://<backend-host>/stats`) — server-rendered HTML listing top **domaines (roles)**,
  **problématiques (Q3)**, **cas d'usage consultés**, and total **clics bouton parcours**
  (the key conversion). JSON at **`/api/v1/stats.json`**.
- **How it records:** `backend/app/stats.py`. Each event is appended to an **Azure append blob**
  (`stats/events.jsonl`) when `STORAGE_ACCOUNT_NAME` / `STORAGE_ACCOUNT_KEY` are set; otherwise it
  falls back to **in-memory** (resets on restart). The append blob is created on first event.
- **Wiring (already done in dev):**
  ```bash
  KEY=$(az storage account keys list -n stavoulia97186 -g rg-avoulia-fr-dev --query "[0].value" -o tsv)
  az containerapp update -n avoulia-backend -g rg-avoulia-fr-dev \
    --set-env-vars STORAGE_ACCOUNT_NAME=stavoulia97186 STORAGE_ACCOUNT_KEY="$KEY"
  ```
  Without these env vars the app still works (memory fallback); with them stats survive restarts.
- **Recording points:** domaine (at selection) + problème (free-text Q3 that yields the case list)
  in `routes/chat.py::_record_usage_stats`; cas (when the verbatim card opens) in
  `haystack_rag.py::stats.record("cas", …)`; parcours_click via `POST /api/v1/chat/parcours-click`
  called fire-and-forget by the frontend (`chat.ts::trackParcoursClick`, wired in
  `HomeView.vue::onParcoursClick`).
- **Reset:** delete the blob to start clean —
  `az storage blob delete --account-name stavoulia97186 --account-key "$KEY" --container-name stats --name events.jsonl`.
- **Compatible with the future single-container packaging** (no new infra; FastAPI serves `/stats`).

### Case feedback 👍/👎 (Axe 3.2)
- Below each case card, two buttons ask "Ce cas vous semble-t-il pertinent ?". A click posts to
  **`POST /api/v1/chat/feedback`** (`{useful: bool, case_label}`) which records `feedback_up` /
  `feedback_down` with the case's **verbatim title** (`cas_utilisation`). One vote per card, then a
  thank-you replaces the buttons.
- The `/stats` page shows a **satisfaction KPI** (`N👍 / M👎`) plus two rankings: cases rated useful
  and cases rated not-relevant — a quality signal to prioritise improving the use-case base.
- Frontend: `chat.ts::sendCaseFeedback` (fire-and-forget), wired in `HomeView.vue::onCaseFeedback`.
  The clean label comes from `suggested_cases[].cas_utilisation` (already in the SSE payload), NOT
  the raw `content` (which is the pipe-delimited rag_text).

---

## ⚙️ CI/CD & déploiement (2026-08-31)

**CI (automatique, sans secret) —** `.github/workflows/ci.yml` tourne à chaque push/PR sur `main` :
- **backend** : `pip install -r requirements.txt` → `python -m compileall app` → `python -m unittest`.
- **frontend** : `npm ci` → `npm run type-check` → `npm run check:dead` → `npm run build-only`
  (+ lint informatif, `continue-on-error`).

Cette CI **ne déploie rien** — c'est un garde-fou : si le code ne compile pas, qu'un test casse ou
qu'un composant Vue est mort, la CI passe au rouge **avant** tout déploiement.

**Détection de code mort —** `frontend/scripts/check-dead-code.mjs` (`npm run check:dead`) échoue si
un `.vue` de `src/` n'est importé nulle part (exception : `App.vue`). Objectif : ne plus jamais
rééditer un fichier fantôme (le bug `ChatView.vue` a coûté cher). Le scaffolding Vite mort
(HelloWorld / TheWelcome / WelcomeItem / `icons/*`) a été supprimé.

**Déploiement (aujourd'hui, manuel) —** build ACR + update Container App :
```bash
# Backend (toujours avec CACHEBUST pour éviter la couche COPY en cache)
az acr build --registry acravoulia97186 --image avoulia-backend:<tag> \
  --build-arg CACHEBUST=$(date +%s) backend/
az containerapp update -n avoulia-backend -g rg-avoulia-fr-dev \
  --image acravoulia97186.azurecr.io/avoulia-backend:<tag>
# Frontend (idem sans CACHEBUST)
az acr build --registry acravoulia97186 --image avoulia-frontend:<tag> frontend/
az containerapp update -n avoulia-frontend -g rg-avoulia-fr-dev \
  --image acravoulia97186.azurecr.io/avoulia-frontend:<tag>
```
**Pour ajouter le CD (déploiement auto) plus tard :** créer un service principal / OIDC côté tenant
Simplon, stocker les identifiants en **secrets GitHub**, et ajouter un job `deploy` (needs: [backend,
frontend]) qui rejoue les commandes ci-dessus puis `node smoke-test.mjs`. Volontairement **non
branché ici** car les identifiants sont spécifiques au tenant d'hébergement (Simplon).

**GitHub Pages —** `.github/workflows/pages.yml` publie le frontend statique sur Pages (vitrine) ;
distinct du déploiement applicatif sur Container Apps.

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| Bicep deployment fails | Check Azure CLI auth + RG exists + correct parameters |
| No telemetry data | Verify `APPINSIGHTS_INSTRUMENTATION_KEY` is valid; check browser console for JS errors |
| Parcours URL always 404 | Verify `AVOULIA_SALT` matches prod environment; check hash generation logic |
| Dashboard shows no data | Wait 5-10 min for events to flow; check KQL query syntax in Logs |
| App Insights quota exceeded | Check data retention settings (prod = 90 days); consider sampling rate |
| Cases from wrong intention appear, or fewer selectable cases than displayed | See "Known Issues Fixed (2026-08-25)" above — check for a silent fallback reintroducing off-topic docs in `haystack_rag.py` |
| Parcours button missing after selecting a case | Backend must send top-level `parcours_url` in the `done` payload — see "Parcours CTA — Backend Is Authoritative (2026-08-26)". Don't rely on frontend index matching |
| `'ChatMessage' object has no attribute 'strip'` | Extract reply text via `_reply_to_text()`; the Haystack chat API returns `ChatMessage` (text via `.text`) — see "Haystack Chat Generator API (2026-08-26)" |
| Duplicated `🚀 Passez à l'action` block after case selection | The parcours pitch was appended twice. Both append sites are now idempotent via `PARCOURS_PITCH_SENTINEL` (`parcours_util.py`) |
| A code fix is in the deployed `.py` (confirmed by `grep` in the container) but prod still shows the OLD behavior | **Stale Python bytecode.** Old `__pycache__/*.pyc` (even from a different Python version, e.g. a dev machine's `cpython-314.pyc`) shipped in the image and ran instead of the up-to-date source. The `backend/Dockerfile` now purges `__pycache__` after `COPY app` and sets `PYTHONDONTWRITEBYTECODE=1`. Never copy/commit `__pycache__` into the build context |
| The deployed `.py` ITSELF is stale (grep in the container shows old source, though the local file is up to date) | **Cached `COPY` layer in the ACR build.** `backend/Dockerfile` has `ARG CACHEBUST` before `COPY app`; always build with `--build-arg CACHEBUST=$(date +%s)` (or the image tag / git commit) so the code copy is redone from scratch |
| A frontend change doesn't appear in the built bundle (same JS hash every build) | The edited component may be **dead code** (not imported anywhere) and tree-shaken out. The live chat UI is **`frontend/src/views/HomeView.vue`**, NOT `ChatView.vue` (deleted). Verify with `grep -r ComponentName src/`. Edit `HomeView.vue` for chat/CTA changes |
| Users don't see a new deployment (old JS keeps loading) | `index.html` must be served `no-cache` so browsers re-fetch it and pick up the new content-hashed assets. See `frontend/nginx.conf` (`location = /index.html`) |
| `/stats` is empty or resets on restart | The stats append blob isn't configured — set `STORAGE_ACCOUNT_NAME` / `STORAGE_ACCOUNT_KEY` env vars on the backend container app (see "Usage Stats" section). Without them, stats use an in-memory fallback that resets on each restart |


---

## 📞 Contact & Support

**Questions about V2 implementation?**
- Review files in `infra/` and `backend/` directories
- Check `SUIVI_PROJET.md` for decisions and architecture notes
- Reference template implementations in `CHANTIER_*.py` files

**Critical constraints:**
- ⚠️ **AVOULIA_SALT must never rotate in production** (all hashes depend on it)
- ⚠️ **Case IDs must be verbatim from Excel** (no reformulation by LLM)
- ⚠️ **Parcours pages must be non-indexed** (`X-Robots-Tag: noindex`)

---

**Last Updated:** 2026-07-10  
**Prepared by:** Eneric (with Copilot)
