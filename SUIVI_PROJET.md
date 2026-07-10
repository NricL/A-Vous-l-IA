# Avoulia V2 — Suivi Projet & Décisions

**Date de démarrage:** 2026-07-08  
**Statut global:** Chantiers A/C/D/E ✅ Complétés — Prêt pour handover Simplon  
**Tenant cible:** Production Azure (westeurope, tenant officiel)  
**Repo:** `NricL/A-Vous-l-IA` (privé — source unique)

---

## 📐 Vision & Architecture

### Objectif V2
Ajouter au système Avoulia existant (backend RAG + frontend Vue) :
1. **Parcours pages** — Guidance step-by-step post-diagnostic (6 étapes ~ 2.5h)
2. **Telemetry** — Tracking complet du funnel chat → RAG → parcours → completion
3. **Dashboard** — KQL queries + Azure Workbook pour monitoring

### Flux utilisateur complet
```
PME accède chatbot
    ↓ [TELEMETRY: chat_session_start]
Pose question libre
    ↓ [TELEMETRY: user_message_sent]
Backend RAG cherche cas dans Excel + retourne réponse
    ↓ [TELEMETRY: rag_result_returned]
Chatbot propose URL parcours
    ↓ [TELEMETRY: parcours_url_proposed]
PME clique sur URL → Page parcours
    ↓ [TELEMETRY: parcours_page_opened]
Étape 1: PME valide cas (3 questions)
    ↓ [TELEMETRY: parcours_step_1_completed]
Étapes 2-6: PME effectue actions de mise en œuvre
    ↓ [TELEMETRY: parcours_step_*_completed]
Quick win: Option copy/test prompt
    ↓ [TELEMETRY: quickwin_copy/open/close]
Session end
    ↓ [TELEMETRY: chat_session_end]
Dashboard agrège tous les événements → Funnel, retention, bounce rate
```

### Contraintes non-négociables
- ⚠️ **Restitution verbatim octet-pour-octet** des champs Excel (jamais reformuler LLM)
- ⚠️ **Pré-filtrage métadonnées** AVANT recherche vectorielle (domaine, secteur, intention)
- ⚠️ **Parcours non-indexées** (`X-Robots-Tag: noindex`, meta noindex)
- ⚠️ **AVOULIA_SALT fixe en prod** — rotation = 404 cascade (toutes hashes changent)
- ⚠️ **Base Excel privée** — jamais exposée publiquement

---

## 📊 Décisions prises (D1-D7)

| ID | Sujet | Décision | Rationale | Statut |
|---|---|---|---|---|
| **D1** | Restitution données | Verbatim octet-pour-octet, pas reformulation LLM | Confiance PME + compliance | ✅ Validée |
| **D2** | Pré-filtrage metadata | Avant vector search (domaine/secteur/intention) | Réduit bruit + améliore pertinence | ✅ Validée |
| **D3** | Base Excel protégée | Jamais exposée publiquement ; accès via API seulement | Sécurité données clients | ✅ Validée |
| **D4** | Plateforme pilote | Azure Static Web Apps (parcours pages statiques) + SWA Deployment | Free tier, itération rapide | ✅ Déployée |
| **D5** | UX Reordering | Étape 1 (validation) en haut → Quickwin en bas accordion | Psychology: valider d'abord, engagement mental | ✅ Implémentée (commit 99d5cbb) |
| **D6** | Chantiers A/C/D | Config paramétrisée + Bicep IaC + App Insights 8 events + KQL 8 queries | Production-ready, handoff-easy | ✅ Créés |
| **D7** | Chantier E (mapping) | Load `mapping_uc_hash.csv` depuis Azure Blob Storage (vs hardcoded) | Clean, scalable, versioned | ✅ Approuvée |

---

## 📁 Chantiers & Livrables

### Chantier A: Configuration & Infrastructure as Code

#### A.1 — Config Files ✅
- **Files:**
  - `config/environments/dev.perso.json` — Params dev (francecentral, rg-avoulia-fr-dev)
  - `config/environments/prod.officiel.sample.json` — Template prod (westeurope, rg-avoulia-fr-prod)
- **Content:** Environment-specific settings (region, resource names, SKUs, retention)
- **Status:** ✅ Created

#### A.2 — Bicep IaC ✅
- **File:** `infra/main.bicep`
- **Deploys:**
  - Log Analytics Workspace (30/90 days retention)
  - Application Insights (tied to LAW)
  - Storage Account + Blob Container (for mapping CSV)
- **Outputs:** Instrumentation key, connection string, storage key
- **Status:** ✅ Created

#### A.3 — Deployment Guide ✅
- **File:** `HANDOFF.md` (Phase 1: Azure Infrastructure)
- **Instructions:** Step-by-step Bicep deployment + outputs capture
- **Status:** ✅ Created

---

### Chantier B: Parcours Pages (Pilot Phase)

**Status:** ✅ COMPLETE (deployed 2026-07-10)
- 28 parcours pages live on SWA
- UX reordered (Étape 1 first, quickwin bottom accordion)
- All pages HTTP 200, noindex headers, verbatim verified
- CI/CD pipeline: SWA GitHub Actions workflow

**Note:** Pilot uses 28 sample cases from `pilote.txt`. Production will regenerate 1025 pages from full Excel.

---

### Chantier C: App Insights Instrumentation ✅

#### Frontend Telemetry
- **File:** `frontend/src/appinsights-instrumentation.html`
- **Events tracked:**
  1. `chat_session_start` — Page load (chatbot)
  2. `user_message_sent` — PME asks question
  3. `rag_result_returned` — Backend returns case
  4. `parcours_url_proposed` — Chatbot shows URL link
  5. `parcours_page_opened` — PME clicks parcours URL
  6. `parcours_step_*_completed` (1-6) — Étape completion
  7. `quickwin_copy` — Quick win copy action
  8. `quickwin_open/close` — Accordion toggle
- **Attributes:** Session ID (sessionStorage hash), Case hash, Score, Timestamps
- **RGPD:** No cookies, no persistent ID, no IP, no PII; anonymous session hash
- **Status:** ✅ Created

#### Integration Points
- Import snippet into `frontend/index.html` `<head>` OR `frontend/src/main.ts`
- Add `data-case-hash="{{ case_id }}"` to parcours page body
- Ensure `VITE_APPINSIGHTS_INSTRUMENTATION_KEY` env var is set (GitHub Secret)

---

### Chantier D: Analytics & Dashboard ✅

#### KQL Queries
- **File:** `infra/kql-queries.kql`
- **Queries (8):**
  1. **Funnel completion %** — Chat → RAG → Parcours → Step 1 → Step 6
  2. **Top 10 cases** — Most visited parcours pages
  3. **Quickwin copy rate** — % sessions with copy action
  4. **Retention (J+1/3/7)** — Returning sessions
  5. **Mode execution split** — Outil vs no_code (needs mapping join)
  6. **Timeline** — Events per hour (last 24h)
  7. **Bounce rate** — Chat start → no RAG hit
  8. **Avg steps completed** — Per session median
- **Status:** ✅ Created

#### Azure Workbook
- **File:** `infra/dashboards/avoulia-parcours-dashboard.json`
- **Panels:**
  - Funnel completion % (stacked column)
  - Top 10 cases (table)
  - Quickwin engagement (donut)
  - Events timeline (area chart, last 24h)
- **Status:** ✅ Created

#### Deployment
- Import via CLI: `az monitor workbooks create --definition @infra/dashboards/avoulia-parcours-dashboard.json`

---

### Chantier E: Backend Enhancement ✅

#### Endpoint Modification
- **File:** `backend/CHANTIER_E_BACKEND_ENDPOINT.py` (template)
- **Change:** Chat endpoint `/api/v1/chat` returns:
  ```json
  {
    "answer": "Steps Q2-Q3",
    "case_id": "UC-0042",
    "case_hash": "vn38reuyw7",
    "parcours_url": "https://avoulia.azurewebsites.net/action/vn38reuyw7/",
    "matching_score": 0.92
  }
  ```
- **Hash generation:** Deterministic via `SHA256(case_id + AVOULIA_SALT)`
- **Key env vars:**
  - `AVOULIA_SALT` — Fixed forever (prod)
  - `PARCOURS_BASE_URL` — Hardcoded domain
  - `APPINSIGHTS_INSTRUMENTATION_KEY` — For backend telemetry (optional)

#### Mapping Strategy
- **Option 1 (Current):** Deterministic hash generation (no storage needed)
- **Option 2 (Future):** Load mapping CSV from Blob (`mapping_uc_hash.csv` in `parcours-mappings` container)
  - If using: backend queries Blob on startup, caches in memory
  - Migration: Pre-generate CSV from Excel, upload once

- **Status:** ✅ Template created; implementation needed (Phase 2 for Simplon)

---

### Handover & Documentation ✅

- **File:** `HANDOFF.md`
- **Content:**
  - Overview (flow, components)
  - Phase 1: Azure Infrastructure (Bicep)
  - Phase 2: Backend enhancement (chat endpoint)
  - Phase 3: Frontend integration (telemetry)
  - Phase 4: Parcours pages (reference)
  - Phase 5: Dashboard setup
  - Environment variables table
  - Validation checklist
  - Troubleshooting guide
- **Status:** ✅ Created (production-ready for handover to Simplon)

---

## 🔄 Dependencies & Roadmap

### Completed (Chantiers A-D)
```
[Config Files (A1)] ✅
        ↓
[Bicep IaC (A2)] ✅
        ↓
[App Insights (C)] ✅
        ↓
[KQL Queries (D)] ✅
        ↓
[Workbook Dashboard (D)] ✅
```

### Ready for Next Phase
```
[Backend Enhancement (E)] → Implement chat endpoint (Simplon)
        ↓
[Integration Testing] → Verify telemetry flow
        ↓
[Production Deployment] → Deploy to prod tenant
        ↓
[Monitoring & Optimization] → Monitor funnel metrics, tune retention
```

---

## 📈 Success Metrics (Post-Launch)

| Metric | Target | Measurement |
|---|---|---|
| **Funnel completion** | >50% (chat → RAG) | KQL Query #1 |
| **Parcours page open rate** | >40% (from chat) | KQL Query #1, funnel_step3 |
| **Step 1 completion** | >70% (of opens) | KQL Query #1, funnel_step4 |
| **End-to-end (step 6)** | >30% (of opens) | KQL Query #1, funnel_step6 |
| **Quickwin engagement** | >20% (copy/test) | KQL Query #3 |
| **Retention (J+1)** | >15% | KQL Query #4 |
| **Bounce rate** | <20% | KQL Query #7 |
| **Avg steps** | >3 (median) | KQL Query #8 |

---

## 🚀 Deployment Checklist (For Simplon)

### Pre-Deployment
- [ ] Code review: backend changes (chat endpoint), frontend integration
- [ ] Security review: RGPD, AVOULIA_SALT, storage access
- [ ] Testing: local E2E (chat + parcours + telemetry)

### Deployment
- [ ] Bicep: Deploy infrastructure to prod RG
- [ ] Secrets: Set all env vars in Container Apps / Key Vault
- [ ] Backend: Build & push new image to ACR, update Container App
- [ ] Frontend: Build & deploy (App Insights key injected)
- [ ] Pages: Generate 1025 parcours pages, upload to hosting

### Post-Deployment
- [ ] Smoke test: Chat endpoint returns parcours URL
- [ ] Telemetry: Events flowing to App Insights (5-10 min delay)
- [ ] Dashboard: Workbook shows data, KQL queries non-empty
- [ ] Monitoring: Set up alerts (e.g., bounce rate > 30%)

---

## 📝 Journal

- **2026-07-08** — V2 project initiated; clarified requirements (telemetry chat → parcours)
- **2026-07-09** — Designed chantiers roadmap (A/C/D/E)
- **2026-07-10 17:48** — UX reordering decision (D5); template updated, deployed to SWA
- **2026-07-10 18:38** — Chantiers A/C/D/E created:
  - A1: Config files (dev/prod)
  - A2: Bicep IaC
  - C: App Insights snippet (8 events, RGPD-safe)
  - D: KQL queries (8) + Workbook JSON
  - E: Backend endpoint template
- **2026-07-10 18:45** — HANDOFF.md created (production-ready guide for Simplon)

---

## 🔐 Security & Compliance Checklist

- [ ] **Verbatim compliance:** No LLM reformulation of Excel fields
- [ ] **Metadata filtering:** Pre-filter domain/intention BEFORE vector search
- [ ] **Excel protection:** Never expose base publicly; API access only
- [ ] **AVOULIA_SALT:** Fixed forever in prod; never rotate (hash stability)
- [ ] **Noindex headers:** All parcours pages have `X-Robots-Tag: noindex`
- [ ] **RGPD:** No cookies, no persistent ID, no IP logging (Azure masks); session hash only
- [ ] **Secrets management:** Key Vault (prod), GitHub Secrets (dev)
- [ ] **Access control:** Storage access via SAS/connection string (no hardcoded keys)

---

## 📞 Questions & Escalations

**Q:** Can we rotate AVOULIA_SALT in production?  
**A:** ❌ NO. All case hashes depend on it. Rotation = 404 cascade. Keep forever.

**Q:** Should backend handle mapping CSV or frontend?  
**A:** Backend (server-side lookup) — cleaner, no exposure of mapping logic. Frontend just displays URL.

**Q:** What if telemetry key expires?  
**A:** Update GitHub Secret + re-deploy frontend. App Insights resources don't expire, key can be regenerated.

**Q:** How to backfill telemetry for old sessions?  
**A:** Can't; telemetry only tracks new sessions. Historical analysis via Excel + manual audit.

---

**Document maintained by:** Eneric (with Copilot assistance)  
**Last updated:** 2026-07-10 18:45 UTC+2  
**Next review:** Post-handover to Simplon (post-implementation)
