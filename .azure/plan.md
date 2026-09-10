# Azure Deployment Plan

## Status

Deployed and verified on DEV (2026-09-10). Target and plan confirmed by Eneric at 10:15 ("Oui, environnement dev"). Backend0045/frontend0023; no official Simplon deployment or package.

## Current deployment result

- ACR builds dd2a (initial backend0044), dd2b (frontend0023), dd2c (final backend0045): Succeeded.
- Backend final immutable image: `acravoulia97186.azurecr.io/avoulia-backend@sha256:9408ae9a6d8ffc1275a6b6c03f5bba5bbfbb59120f14d4b20b87c44b06b414ea`, tag `v2-nomatch-20260910-r2`.
- Frontend: `acravoulia97186.azurecr.io/avoulia-frontend:v2-nomatch-20260910`.
- Final revisions Healthy, traffic100 %. First numeric13 edge found on0044, corrected and retested on0045.
- Live mobile390px: input and send fully within viewport; normal guided path13/BTP/objective4, fiscal no-match, clarification back to meeting notes, ranked list, first detail and correct parcours URL, return to objective. Desktop1240px input/send visible.
- Direct non-stream request on0045: approved no-match message, zero IDs, no pending action, original domain/sector/intention retained.
- Two served-page SHA-256 values unchanged from baseline below; data/pages/pitch inherited by construction, not rebuilt from local workbook.
- Final local tests106 backend,19 frontend; build/typecheck success. No exhaustive production relevance or whole-catalog UX claim.

## 7. Validation Proof — current release

- Follow-up validated after dev E2E: initial numeric domain allowed only with empty/welcome-only history and no selected state. `python -B -m unittest discover -s tests -q`: 106 passed; real welcome → 13 → BTP tests for HTTP/SSE with and without client state. New backend tag `v2-nomatch-20260910-r2`, same pinned base image and two-file overlay. Frontend remains0023.
- `python -B -m unittest discover -s tests -q` from backend: 104 passed, including both no-match paths and clarification recovery.
- `npm run check:chat`: 19 passed, including no-match previous-step navigation; `npm run build`: build/typecheck succeeded (existing bundle-size warning).
- `git diff --check`: passed.
- Read-only `az containerapp show` for both existing apps: confirmed France Central target and rollback images; `az acr show`: provisioning Succeeded.
- `az acr manifest show-metadata`: pinned inherited backend digest as recorded below.
- SHA-256 comparisons: config.py, rag_constants.py, models.py, rag.py, stats.py and telemetry.py match prior deployed-source snapshot; no new runtime dependency introduced by the two Python files overlaid.
- Backend build staging contains only Dockerfile plus those two Python files; no workbook, generated page, mapping, secret or unrelated artifact uploaded as source context.
- Baseline served-page SHA-256: action-8kn25a5yeq.html = C2770D288E0C66DAE31BF2B6FB6F732E5E6CB1B506104899079E16912C5DD3F1; action-39c79zu8tc.html = 97C30A00A5DE64F306C7D4DBB2640E464EB8E83D46F44E6C9F333991163F174F.
- No IaC change: Bicep/Terraform validation not applicable to image-only update of existing resources. No packaging for Simplon.

## Current release plan — 10 September

1. Correct evaluation diagnostics so numbered clarification questions do not automatically become invented case lists; preserve detection of genuine unknown candidates.
2. Improve the no-match response: no invented/selectable cases, explicit scope limit, invite clarification or use of existing previous-step controls; never silently change filters.
3. Run existing backend/frontend regression tests and targeted review, then Azure validation before deployment.
4. Deploy only to existing development Container Apps, preserve current deployed workbook, static pages, mapping and secrets. Do not rebuild from the repository's historical Excel or publish unregenerated parcours changes. Keep the current parcours pitch consistent with unchanged deployed pages in this release.
5. Verify health, synthetic no-match/clarification behavior, normal guided case selection and mobile UI on the deployed development URL. Record exact image/revision, scope and rollback references in project tracking.

Confirmed target: development subscription (identifier retained in private deployment records), region **francecentral**, resource group **rg-avoulia-fr-dev**, existing **avoulia-backend** and **avoulia-frontend**, ACR **acravoulia97186**. No new infrastructure, no official Simplon environment, no package. Supply the subscription explicitly when reproducing a deployment.

Confirmed implementation: backend `Dockerfile.dev-code-only` overlays only `app/haystack_rag.py` and `app/routes/chat.py` on deployed backend digest `sha256:9d885637d00ded89af891807e0173e1772dc513d9ec1ee6a0a82b87ae6894b8a`. Dependencies, documents, Chroma startup, static pages, mapping, and `parcours_util.py` inherited unchanged. Thus CHAT-04/05/06 source/template changes remain NOT deployed; explicitly record this scope. Frontend uses its existing Dockerfile with reviewed mobile/state/no-match-stepper corrections.

Rollback references read on 10 September: backend `avoulia-backend--0000043`, image `acravoulia97186.azurecr.io/avoulia-backend:v2-parcoursfix3-1788183296`; frontend `avoulia-frontend--0000022`, image `acravoulia97186.azurecr.io/avoulia-frontend:v2-cfg-1788165520`. Do not delete/deactivate prior revisions manually.

User-facing response proposed for no reliable match: « Je n'ai pas de cas suffisamment pertinent à vous proposer avec les choix actuels. Vous pouvez préciser votre besoin ou revenir à une étape précédente pour modifier vos choix. » Final wording and routing to be validated locally; no content from private workbook added to this notice.

Excluded: workbook modification or v455, parcours regeneration, Simplon package/production, semantic threshold tuning from unvalidated labels. September source fixes may be included only after confirming no rollback of the already deployed fixes and no publication of stale data/pages.

## September approved scope and release gate

- Approved: targeted chatbot mobile, qualification, ranking and existing parcours UX corrections. Preserve discovery, six steps, verbatim content, metadata prefilters and private source workbook.
- No infrastructure changes, Azure calls, image builds, commits or pushes in this local lot.
- Local validation: 62 backend/synthetic parcours tests, 18 frontend state tests, frontend build/typecheck. Focused code review has no remaining known blockers in its reviewed fixtures; semantic relevance calibration remains partial.
- Before deployment: validate source parity with prior short-content fix; regenerate approved parcours using the separate parcours pipeline, retain mappings and backlinks, and reconcile its directory routes with backend action-<hash>.html routes. Do not substitute legacy backend generator.
- Workbook reference remains cloud-hosted v454 working; partial WorkIQ read only. No workbook changes or v455. Do not regenerate from historical v453 by default.
- Deployment pending: user-visible change preview/confirmation, Azure validation and confirmed target context before any infrastructure or image update.

## Scope

Modify the existing Avoulia backend Container App with the Haystack chat-generator compatibility fix.

## Architecture

- Backend: Python FastAPI container
- Platform: Azure Container Apps
- Resource group: `rg-avoulia-fr-dev`
- Container registry: `acravoulia97186.azurecr.io`
- Deployment recipe: Azure CLI / ACR build

## Deployment steps

1. Build and push the backend image with ACR.
2. Update the existing `avoulia-backend` Container App.
3. Route 100% traffic to the new revision.
4. Verify health and the case-detail flow.

## Validation Proof

Validation completed:

- `python -m py_compile backend\app\haystack_rag.py` — passed.
- `az account show` — authenticated subscription confirmed.
- `az containerapp show -n avoulia-backend -g rg-avoulia-fr-dev` — target succeeded and 100% traffic on latest revision.
- `az acr task show-run --registry acravoulia97186 --run-id dd1b` — image build succeeded.
- `az containerapp update ...` — revision `avoulia-backend--0000029` succeeded.
- `curl https://avoulia-backend.purpleocean-980317d1.francecentral.azurecontainerapps.io/health` — `{"status":"ok"}`.
