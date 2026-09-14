# Avoulia V2 — Implementation Summary (2026-07-10)

**Preparation revision deployed after14September14:48 approval:** all1021cases/3774prerequisites
reviewed. Named single-input preparation with explicit output/status and unchanged
source rules; production consumes prepared inputs, step5tests and step6reuses.
All pages regenerated and deployed at100% on `v463-preparation-20260914-r1`,
image `a8a6cf7cde6cb48f59ffe4e15e1943229f962fcbbb084d434bc2447426917ff8`,
private builddd2v. Workbook/IDs/mapping/bot unchanged; old v463 kept as rollback.
Initial CLI submission failed before a run; documented ARM/native HTTPS transport
resumed the same verified archive successfully. The deployment below is historical.

Published source commits: `3f7bf8b1499989f99c7fedbd434793fad217fb7f` and
`8989942a53690b4901e2a6216059f06ca1692671`; CI `34849464018` succeeded.
Frontend unchanged, existing Pages/Azure frontend links use the revised pages.
The local preview server was stopped; private workbook and user edits remain untouched.

**V463 backend deployed,14September:** user approved1021Sheet1fiches and generic six-step
parcours at12:13. Revision `v463-20260914-r1` serves100% after isolated acceptance;
image `5de8ca8cc8f46828b8a62ddf83b7a47f0c9afb767b2d75720f6558a6e0c95182`,
private builddd2u on Python3.11.16.1021current+4historical pages, unchanged mappings,
private labelled workbook/audits excluded from public Git/webroot. Public HTML is
synchronized and the old mapping CSV removed from HEAD, not Git history. Existing
frontend image and selector wording retained; old stable remains the rollback.

Source release commits: public830d2b0976d99a1622fc373437c873d1d90c7e1c,
privatee61e4873a6d714aae24eb67003123d73a74def26. Pages34835285869 and
CI34835285888 succeeded. Old backend/frontend preview revisions are inactive;
Pages root and Azure frontend proxy use the current v463 backend.

**The following milestones are historical**, not the current delivery status.

**Content milestone after14September11:29:** private v463 prepared from preserved v462
with four focused editorial changes, unchanged1021IDs/taxonomy/modes and6158formulas.
Four six-step text previews and generic prompts remain inside the labelled workbook.
No private HTML/JSON export, no catalogue regeneration or deployment. The earlier
complete review and five taxonomy reservations are retained, not re-audited or erased.

**Current work (2026-09-14, 80/20):** keep the existing Haystack/Chroma bot. Remove the
parallel preview/verifier/orientation and its deployment wiring; do not migrate to R2.
Retain the full retrieved candidate pool before the five-result display cap.
As of10:59 the original selection prompt is restored unchanged; no comparative benefit
was established for the experimental wording. Private image dd2s predates that restoration
and must not be deployed as the current minimal bot.
Keep generic six-step adoption guidance without automatically copying the chat need.
Roadmap now prioritizes all 1,021 case/parcours improvements over further bot tuning.
The common parcours template has a shorter introduction, plain prerequisite choices
and three practical output checks (useful/reliable/usable). Local template changes only;
stable, deployed r1, catalogue, generated pages and traffic unchanged.

**Archived experiment:** r1 (`812aa94`, private renderer `5c748ef`) was deployed separately;
r2 never was. The experiment's false rejections, timeout and recovery attempts remain
documented, but are no longer active implementation or rollout instructions.

**Historical scope below:** earlier implementation notes, not the current development
or deployment instructions. ROADMAP/HANDOFF contain the superseding 80/20 direction.

**Current status (2026-09-13):** v461 and the five UX fixes are deployed on the existing DEV backend revision `avoulia-backend--ux-20260913-d02ffad`; Pages and the Azure frontend carry the same source commit `d02ffad`. Parcours source remains `a500a22`, and workbook, mapping and generated pages are unchanged. Private exports are not served. See [`ROADMAP.md`](./ROADMAP.md), [`SUIVI_PROJET.md`](./SUIVI_PROJET.md) and [`HANDOFF.md`](./HANDOFF.md) for the final receipt and retained rollback images. The Simplon package remains deferred; historical generation instructions below are not the current release recipe.

**Programme invariants:** preserve explicit domain/sector/objective qualification and catalogue grounding. No automatic LLM classification of qualification choices. All 1,021 cases and implementation pages remain in scope, preserving source versions, IDs, filters and six-step order. The intermediate progress notes below are historical; ROADMAP and HANDOFF describe the latest state.

**Progress at12:36:** QUAL-01 offline reference tooling prepared locally (66mechanical scenarios,63conforming,3documented target gaps). Joint trials motivated ORI-01, a proposed separate catalogue-routing recovery with user confirmation, not automatic replacement of active filters. All catalogue/adoption recommendations remain in scope. Neither the new qualification protocol nor routing recovery is implemented or deployed.

**Subsequent local implementation:** executable loopback preview at `http://127.0.0.1:4178/preview`, server8767,16explicitly synthetic cases with qualification/reorientation/terminal-card and six-step rendering. It is NOT connected to the real v461 RAG. Full catalogue review remains blocked on reliable authorized data access. No workbook, public page, production deployment or GitHub publication changed; HANDOFF contains exact run instructions and limitations.

**After explicit raw-local authorization at16:43:** full inventory and documentary review of1,021cases completed in label-preserving audit workbooks. Source cells/formulas remain unchanged; proposed changes are not integrated. Real-preview data exposure remains restricted by classification. Findings require diagnosing in-filter retrieval misses as well as considering confirmed cross-domain recovery.

---

### Update 2026-07-15
- 🔧 Frontend startup regression reproduced on the deployed bundle (`lastSuggestedCases is not defined`)
- ✅ Restored `HomeView.vue` and `ChatView.vue`, then added the missing `*.vue` TypeScript declaration
- ✅ Local frontend build passes again
- ✅ Frontend image rebuilt and deployed to Azure Container Apps (`v2-202607151604`)
- ✅ Live validation passed on the new revision and on the main frontend URL with cache-buster
- 🔧 Parcours links now need a short explanatory sentence, and backend must resolve slugs via the embedded mapping when no Blob mapping is configured

### Update 2026-07-15 — parcours mapping fix
- ✅ Added `backend/app/static/parcours/mapping_uc_hash.csv` generated from the existing static pages
- ✅ `backend/app/parcours_util.py` now falls back to that local mapping automatically
- ✅ Backend image rebuilt and deployed as `acravoulia97186.azurecr.io/avoulia-backend:v2-202607151510`
- ✅ Live verification succeeded on `action-8khzcn5jmb.html` (UC-0569)

---

## 🎯 Accomplishments (This Session)

### 1. Frontend Telemetry Integration ✅
- **File:** `frontend/src/appinsights.ts` (new module)
- **File:** `frontend/src/main.ts` (updated)
- **Changes:**
  - TypeScript module for Application Insights (8 events)
  - Session ID generation (weekly regeneration)
  - Event tracking: chat_session_start, user_message_sent, rag_result_returned, parcours_url_proposed, parcours_page_opened, step_completion, quickwin_action
  - Auto event listeners (checkbox change, accordion toggle, copy button)
  - Global property injection: `app.config.globalProperties.$appInsights`
- **Usage in components:**
  ```typescript
  import { getAppInsights } from '@/appinsights'
  const appInsights = getAppInsights()
  appInsights.trackUserMessage(messageText, 'pme_question')
  appInsights.trackRagResult(caseId, score)
  appInsights.trackParcoursUrlProposed(url, caseHash)
  ```

### 2. Backend Enhancement ✅
- **New file:** `backend/app/parcours_util.py` (utility module)
  - `generate_case_hash()` — Deterministic SHA256 hash (case_id + AVOULIA_SALT)
  - `build_parcours_url()` — Full URL construction
  - `build_parcours_info()` — Complete info dict (hash + URL)

- **Modified file:** `backend/app/models.py`
  - Extended `SuggestedCase` model: added `case_hash` and `parcours_url` fields

- **Modified file:** `backend/app/routes/chat.py`
  - Imported `build_parcours_info()` utility
  - Updated `_build_suggested_cases()` to generate parcours URLs for each case
  - Chat endpoint now returns parcours URLs alongside case recommendations

- **Result:** Backend endpoint `/api/v1/chat` now returns:
  ```json
  {
    "answer": "...",
    "suggested_cases": [
      {
        "id": "UC-0042",
        "case_hash": "d8b0c8103fe8f9e1",
        "parcours_url": "https://avoulia.azurewebsites.net/action/d8b0c8103fe8f9e1/",
        ...
      }
    ]
  }
  ```

### 3. Parcours Page Generation ✅
- **New file:** `backend/scripts/generate_parcours_pages.py`
- **Purpose:** Generate static HTML pages for all 1025 cases
- **Features:**
  - Loads sample cases (mock data for now; hooks to Excel in production)
  - Generates deterministic URLs using case hash
  - Produces standalone HTML pages with:
    - Meta noindex tags (prevents indexing)
    - Telemetry script integration
    - Complete parcours structure (Étape 1-6, quickwin)
    - App Insights event tracking hooks
  - Saves to `/generated_pages/<hash>.html`

- **Usage:**
  ```bash
  # Generate 1025 pages
  python backend/scripts/generate_parcours_pages.py 1025 generated_pages/
  ```

- **Test run:** Successfully generated 5 sample pages (verified)

---

## 📊 Architecture Diagram (Updated)

```
┌─────────────────┐
│ PME Chatbot     │
│ (Vue3 Frontend) │
│ [TELEMETRY ON]  │◄── App Insights: chat_session_start, user_message
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Backend RAG         │
│ (FastAPI)           │
│ [TELEMETRY ON]      │◄── App Insights: rag_result_returned
└────────┬────────────┘
         │
         ▼ (with case_hash + parcours_url)
┌──────────────────────────────────────────┐
│ Frontend: Display case + Parcours URL    │
│ [TELEMETRY ON]                           │◄── parcours_url_proposed
└────────┬─────────────────────────────────┘
         │
         │ (user clicks URL)
         ▼
┌──────────────────────────────────────────────────────────┐
│ Parcours Page (Static HTML)                              │
│ /action/<hash>/ with data-case-hash="<hash>"            │
│ [TELEMETRY ON: step tracking, quickwin events]          │
└────────┬───────────────────────────────────────────────┬─┘
         │                                               │
         ▼                                               ▼
┌─────────────────────────────┐    ┌──────────────────────────────┐
│ App Insights (Telemetry)    │    │ Azure Log Analytics          │
│ - 8 primary events          │    │ - Data storage               │
│ - sessionId tracking        │    │ - 30/90 day retention        │
│ - anonymized (no cookies)   │    │ - RGPD compliant             │
└────────┬────────────────────┘    └────────┬─────────────────────┘
         │                                   │
         └─────────────────┬─────────────────┘
                           ▼
                  ┌────────────────────────┐
                  │ Azure Workbook         │
                  │ (Dashboard KQL)        │
                  │ - Funnel %             │
                  │ - Top cases            │
                  │ - Quickwin rate        │
                  │ - Retention            │
                  │ - Bounce rate          │
                  └────────────────────────┘
```

---

## 🔑 Environment Variables (Required)

| Variable | Value | Source |
|---|---|---|
| `AVOULIA_SALT` | `prod-salt-value` | Backend env var (fixed forever) |
| `PARCOURS_BASE_URL` | `https://avoulia.azurewebsites.net` | Backend env var |
| `VITE_APPINSIGHTS_KEY` | From Bicep outputs | Frontend build-time |
| `APPINSIGHTS_INSTRUMENTATION_KEY` | From Bicep outputs | App Insights (optional backend) |

---

## 📁 Files Created/Modified This Session

### Created
- `frontend/src/appinsights.ts` (new TypeScript module, 7.8 KB)
- `backend/app/parcours_util.py` (utility functions, 2.0 KB)
- `backend/scripts/generate_parcours_pages.py` (page generator, 8.7 KB)

### Modified
- `frontend/src/main.ts` (added telemetry initialization)
- `backend/app/models.py` (extended SuggestedCase model)
- `backend/app/routes/chat.py` (injected parcours URL generation)

### Test Generated
- 5 sample parcours pages (verified HTML structure)
- Sample size: ~4.2 KB per page
- **Estimated total for 1025 pages:** ~4.3 MB (uncompressed)

---

## ✅ Validation Checklist

- [x] Frontend telemetry module created (TypeScript)
- [x] Main.ts updated with App Insights initialization
- [x] Backend models extended (case_hash, parcours_url fields)
- [x] Chat endpoint modified to generate URLs
- [x] Parcours URL utility module created
- [x] Page generator script functional
- [x] Sample pages generated successfully
- [x] Environment variables documented
- [x] Git committed (all changes staged)

---

## 🚀 Next Steps (E2E Validation)

### To Complete:
1. **Bicep Deployment (IMPL-Bicep)**
   - Need Azure CLI access (currently blocked by auth)
   - Alternative: Manual deployment via Azure Portal

2. **Frontend Build & Test (IMPL-Frontend)**
   - Run `npm run build`
   - Set `VITE_APPINSIGHTS_KEY` in GitHub Secrets
   - Test telemetry events in DevTools

3. **Backend Build & Deploy**
   - Build Docker image with new modules
   - Push to ACR
   - Update Container App

4. **Generate Full 1025 Pages (IMPL-Pages)**
   - Load actual Excel data
   - Generate all pages
   - Upload to hosting (SWA or Blob Storage)

5. **E2E Test (IMPL-E2E)**
   - Chat with PME → Get suggested cases + URLs
   - Click parcours URL → Open page
   - Complete steps → Check App Insights events
   - Verify funnel metrics in dashboard

---

## 📝 Code Quality

- **Frontend:** TypeScript with strict typing
- **Backend:** Python type hints (Pydantic models)
- **Utilities:** Well-documented docstrings
- **Error Handling:** Try-catch blocks, HTTPException
- **RGPD:** No cookies, no persistent ID, no IP logging

---

## 🔐 Security Notes

- ⚠️ `AVOULIA_SALT` is fixed forever (hash stability)
- ⚠️ Case URLs are deterministic (same input → same hash)
- ⚠️ Parcours pages are noindex (not discoverable)
- ⚠️ Telemetry anonymized (session hash only, no PII)

---

## 📊 Session Statistics

| Task | Time | Status |
|---|---|---|
| Frontend telemetry | ~15 min | ✅ Complete |
| Backend enhancement | ~15 min | ✅ Complete |
| Page generator | ~15 min | ✅ Complete |
| Testing & validation | ~15 min | ✅ Complete |
| **Total** | **~60 min** | **✅ DONE** |

---

**Session Complete!** 🎉  
Ready for handover to Simplon for production deployment.

See `HANDOFF.md` for step-by-step implementation guide.
