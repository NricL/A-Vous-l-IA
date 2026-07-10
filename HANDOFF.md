# Avoulia V2 — Implementation Handover Guide for Simplon

**Status:** Ready for Handover (2026-07-10)  
**Target:** Deploy Avoulia V2 with Parcours Pages + App Insights Telemetry to Production Azure  
**Audience:** Simplon DevOps / Backend Team

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

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| Bicep deployment fails | Check Azure CLI auth + RG exists + correct parameters |
| No telemetry data | Verify `APPINSIGHTS_INSTRUMENTATION_KEY` is valid; check browser console for JS errors |
| Parcours URL always 404 | Verify `AVOULIA_SALT` matches prod environment; check hash generation logic |
| Dashboard shows no data | Wait 5-10 min for events to flow; check KQL query syntax in Logs |
| App Insights quota exceeded | Check data retention settings (prod = 90 days); consider sampling rate |

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
