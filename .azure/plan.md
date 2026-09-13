# Azure Deployment Plan

## Status

Deployed — UX-01 through UX-05 completed (2026-09-13), following user approval at09:57. Backend `avoulia-backend--ux-20260913-d02ffad` and frontend `avoulia-frontend--ux-20260913-d02ffad` are Healthy and serve100% traffic. Backend mode is Single; previous r3 is inactive, its image and revision definition retained. GitHub Pages and chatbot main carry `d02ffad`; parcours source/payload are unchanged.

## UX deployment receipt — 13 September

- Source commit `d02ffad38720757f53d15b81519d4f282e1b07a5`; Pages34746510034 and CI34746509999 succeeded. No public workbook/mapping/audit was added.
- Native validation used because the azure-validate skill was unavailable in this runtime. Existing dev subscription/resource group/region, current traffic, immutable base and private registry confirmed before build.
- Code-only contexts exported from committed sources:62 files, approximately1.72MB, no workbook/mapping/secrets/bytecode. Runtime backend overlay contains only `haystack_rag.py` and `rag_constants.py`.
- Backend build dd2k succeeded, digest `sha256:058fe52822fea24c4e52e17b27242480f3ab96771b883243d8bad7efb2aaaafb`;212 Python3.11 tests with one Node-only skip,8 parcours reconciliation tests, unchanged private payload1021 current pages plus4 historical pages.
- Frontend build dd2m succeeded, digest `sha256:2ae5e263bb60ecf245c4ad59658de07323a902da858d60c42cb26c22d4cfee18`. Azure bundle `index-xp7O1gel.js`, Pages bundle `index-CuvdZJ9D.js`.
- Candidate staged while r3 retained100% traffic. Version-specific replica-local index `/app/data/chroma-ux-20260913-d02ffad`, collection `documents-ux-20260913-d02ffad`, reconstructed1021 documents from the inherited private workbook. First health request was too early; promotion waited for Healthy and successful candidate checks.
- Candidate and normal URL: four pipe-free consulting Q3 examples in HTTP/SSE, initial retail need reuse, correct source-verbatim detail and mapped URL, off-topic refusal and recovery,9 unchanged page digests,4 private-export404 responses.
- Normal Pages flow at390px: unique selectable case, correct detail/parcours, no horizontal overflow. Rewinding restored a three-case list and selecting its third case opened the correct detail/URL. Azure frontend1280px exercised its real proxy and Q3 successfully.
- Initial ACR invocations had an incorrect local Dockerfile cwd and started no builds. A CLI connection reset occurred after the mode change succeeded; ARM reads established actual state before continuing. Unicode CLI log rendering also failed; control-plane state and filtered startup logs were used instead. The smoke script's overly restrictive detail-ID assertion was corrected to match the existing full-candidate contract, with selected title/source/URL still asserted.
- Prior backend r3 digest `9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b` and frontend v461 digest `dd4598880ea05482eddf5795f81f97e30bfe6b21ff544ecdcfb38e1dadad1930` retained. No infrastructure/model/workbook/mapping/pages changes or Simplon package.
- Subsequent sections describing local work or pending deployment are historical preparation, superseded by this receipt.

## New local UX work — 13 September, 09:27

User authorized documentation reconciliation followed by five fixes: single-case selection, readable Q3 examples, sector/objective-relevant examples, reuse of the initial explicit need, and rejection of recommendations requiring unstated assumptions. Implementation and regression work are local; this is not a new deployment receipt.

Implemented locally: frontend per-message case choices and rewind restoration; backend example eligibility/splitting/limit, explicit-need recognition, and selection prompt conditions. Targeted regressions:171 backend and31 frontend; frontend build/types and real built UI with synthetic SSE at390/1280px. New synthetic `stock-assumptions` evaluation suite completed eight calls on the existing model: all eight matched engineering expectations, no truncation/transport failures, reversed candidate order unchanged. Private evidence retained separately. Local Python3.14 warnings remain; no new Python3.11 image validation or deployment is claimed.

Future candidate build must use `Dockerfile.dev-catalogue-code-fix` on the current r3 immutable digest. Include both `app/haystack_rag.py` and `app/rag_constants.py` in the minimal app overlay, plus updated tests/evaluation script in the validation package. Do not use the September10 two-file recipe, which omits rag_constants. Do not copy the whole working tree or old workbook/static data into the context. Existing replica-local index can rebuild on a new replica even though its catalogue is unchanged.

Preserve v461 workbook, index, private mapping, generated pages, environment and previous images. No infrastructure, model or Simplon packaging change. Any future outbound publication needs its exact preview and confirmation; the approvals and validation receipts below belong to the already completed release, not this new lot.

## Frontend completion receipt — 13 September

- Chatbot `main`: `24e145b0b75ab43feb5aec9fd6df5c51af33809e`; parcours `main`: `a500a2273318fcf09536807e9bb28517e51c9d49`. Both fast-forward pushes succeeded; no private workbook or mapping added.
- Pages `34743193980` and CI `34743193992` succeeded. CI:167 unittest entries with3 external-repository class skips,20 frontend state tests, types and build successful. Existing informational lint issues remain.
- Frontend ACR build `dd2j` succeeded, digest `sha256:dd4598880ea05482eddf5795f81f97e30bfe6b21ff544ecdcfb38e1dadad1930`, tag `v461-20260913-85cd9f56e7fc4ded8025870fa0f8f347`.
- Azure frontend proxy: welcome JSON and streaming domain selection passed, including the metadata-derived hotel sector. Backend revision/image still r3/`9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b`.
- Browser checks on Pages and Azure frontend show1,021 cases,14 business domains,71 intentions. At390px input/send remain visible without horizontal overflow. Pages bundle `index-C7H9OISj.js`; Azure bundle `index-CNyu_LPU.js`.
- The container build used the unchanged lockfile. npm reported18 dependency advisories; they were not assessed or automatically fixed in this label-only release. Local Azure CLI log rendering failed on a Unicode checkmark, but the registry control-plane build status/digest and live image were verified successfully.
- No backend deployment, index rebuild, workbook change or parcours workflow execution occurred during this frontend finalization. Previous frontend image retained for rollback.

## Frontend finalization — validation proof, 13 September

- Exact approved source commit `24e145b0b75ab43feb5aec9fd6df5c51af33809e` published to chatbot `main`; reconciled parcours merge `a500a2273318fcf09536807e9bb28517e51c9d49` published to its `main`, both by non-forced fast-forward.
- User08:35 approval explicitly includes publication on GitHub Pages and the existing Azure DEV frontend. The only new visible frontend labels are1,021 cases and14 business domains.
- `npm run check:chat`, `npm run type-check`, `npm run build-only` rerun on this exact source:20 tests passed, types and build passed. Existing bundle-size warning remains.
- GitHub Pages run `34743193980` and CI run `34743193992`: both succeeded for the approved commit. The parcours deployment workflow remains manual and was not triggered.
- `az containerapp show` confirms frontend0023, France Central, previous image `avoulia-frontend:v2-nomatch-20260910`. The backend is still r3 at its previously validated digest.
- Private frontend build context contains only35 tracked files exported from the approved Git tree; no workbook, mapping, local environment secret or node_modules. Build using the existing frontend Dockerfile in the existing private registry, then deploy by resulting digest.
- Validate new frontend health, bundle labels and API proxy; preserve the previous frontend image for rollback. Do not touch backend/index configuration.

Validated by the active `azure-validate` checkpoint. No new IaC/resource creation is required.

## Final deployment result — 13 September

- Image: `acravoulia97186.azurecr.io/avoulia-backend@sha256:9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b`.
- Registry build: `dd2h`, tag `v461-20260913-r3-034b9f2f4e5c4b1282ed856bef911054`. Code-only overlay on the previously validated v461 payload image; workbook, pages and mapping unchanged by this last fix.
- Reconciled parcours source: merge `a500a2273318fcf09536807e9bb28517e51c9d49`, including the integration branch and the newer remote source, without overwriting unrelated user edits.
- Runtime-image tests: full backend suite (198 entries; the Node-only browser-handler test is skipped in the Python image) plus8 reconciliation tests. Payload checks validate all current pages and retained historical pages, including hashes and private export exclusion.
- The first candidate never received live traffic. The second passed staging but exposed intermittent off-topic selection after promotion; traffic was rolled back to0045 immediately. The final fix separates case selection from qualification instructions, with no arbitrary lexical threshold or model replacement.
- Final candidate and normal live URL both passed real hotel-sector discovery, expected case selection, HTTP/SSE source-verbatim detail, three repeated off-topic refusals, nine representative current/historical page digests and four private-file404 checks.
- GitHub Pages at390px: sector/objective buttons, case/detail/link, six-step page, prompt shortcut/focus and return link verified; no horizontal overflow. Missing page favicon is a non-blocking asset404, not a chat failure.
- Single-revision mode restored. Only r3 remains active; test candidates and0045 are inactive. Old images/revision definitions remain available. Since index storage is replica-local, reactivating an old image can require rebuilding its derived index.
- No workbook, audit export or mapping was pushed to GitHub. The public mapping endpoint found in the old image is now404.

## Approved execution — 13 September

1. Reconcile the approved parcours integration changes with the newer remote source in an isolated worktree; preserve unrelated user edits and published hashes.
2. Generate the authorized case pages from the explicit private source, retaining previous pages only where needed for historical links. Keep the complete mapping outside the public static directory; block sensitive source/export file types from static serving.
3. Build an overlay from the currently deployed immutable backend image, retaining installed dependencies and unrelated runtime code. Include the approved application changes, the private input workbook, private mapping, generated HTML and corrected startup logic; never place source/audit data under the static webroot or in GitHub.
4. Use a new version-specific Chroma directory/collection in the candidate replica. Inspection found a volume declaration but **no container volume mount**: the current index uses replica-local storage. Preserve this storage topology in this release; do not imply persistent Azure Files is in use. Do not clear or reuse the live index. Keep the old image, revision, index and pages available for rollback.
5. Complete the validation checkpoint, build in the existing private registry, stage a revision without replacing live traffic, verify indexing and representative HTTP/SSE/page/mobile flows, then switch traffic. Restore the old revision if readiness or end-to-end checks fail.
6. Keep frontend Pages as the reference URL; deploy frontend only if its bundle actually changes. This is not a Simplon production deployment or package.

Source texts exposed by step 2/5 are the v461 business fields explicitly authorized by the user, not the workbook file, audit history or mapping. Technical integration decisions and tests remain delegated. No new resource group, subscription, region or paid service is proposed.

## 7. Validation Proof — approved 13 September recipe

Validated by the `azure-validate` workflow after reading this plan and executing the following checks. No new IaC/provisioning template is involved; this is an image/configuration update of existing resources.

| Check | Actual command / method | Result |
|---|---|---|
| Confirmed target | `az account show --subscription <confirmed-dev-id>` and `az group show` | Displayed subscription enabled; existing RG in France Central, as confirmed by the user. |
| Existing revision / rollback | `az containerapp show` and `az containerapp revision list` | Backend0045 healthy, 100% traffic, single revision mode; exact image digest pinned below. |
| Registry safety | `az acr show` and `az acr manifest show-metadata` | Registry ready, anonymous pull disabled; inherited digest exists. No source upload to GitHub. |
| Reconciled parcours source | Local merge `a500a2273318fcf09536807e9bb28517e51c9d49` | Both integration and remote wording retained; unrelated original worktree changes preserved. |
| Source regressions | `python -B -m unittest discover -s tests -q` with reconciled `PARCOURS_SOURCE_ROOT` | 193 passed locally, including static export denial and payload identity tests. |
| Reconciliation regressions | `python -B -m unittest discover -s <parcours-release>/tests -q` | 8 passed. |
| Private payload | Explicit generator and `validate_release_payload` | Current pages match catalogue identities; historical mapped pages retained; mapping/source outside the static directory; source unchanged. Exact counts/hashes in private evidence. |
| Source diff | `git diff --check` in both source trees | Passed. |

The live mapping endpoint was found accessible; the new release removes that CSV from the webroot and denies private source/export extensions. Existing hashes are unchanged.

**Build gate:** `Dockerfile.dev-catalogue-release` runs regression tests in the inherited Python 3.11 image, validates the private payload and only then produces the runtime stage. No API keys or model credentials are passed into the build.

**Promotion gate:** pin traffic to0045 before creating the candidate; use candidate-specific index settings and inherited runtime credentials; wait for indexing/startup, check pages/private-file denials and representative HTTP/SSE behavior. Promote only after success; otherwise leave0045 serving. No index deletion or salt rotation.

### Candidate validation and promotion decision — 13 September

- Builds `dd2d` and `dd2e` stopped safely before a runnable release was published: missing validation-script packaging, then inherited private exports detected in the webroot. Both root causes were fixed; inherited exports are preserved outside static serving.
- `dd2f` produced the first candidate, with Python 3.11 tests and payload checks passed. Live validation exposed sector re-questioning by the model. This candidate received **no live traffic**.
- Guided Q1.5/Q2/Q3 questions now come directly from validated server state and catalogue choices. The model no longer revalidates sector membership or renumbers these menus. Local regression suite: 196 passed.
- Corrected build `dd2g` succeeded, image `acravoulia97186.azurecr.io/avoulia-backend@sha256:9d2121d80a5c027faa96279410bead6b90b8ab33ebaaeb20c7db5f49964c67d8`, tag `v461-20260913-r2`; candidate `avoulia-backend--v461-20260913-r2` is Healthy.
- Candidate HTTP checks passed: health; four private-source/export paths return404; nine current/historical page digests match the staged payload. Actual discovery in a previously missing sector, expected case, source-verbatim details in HTTP/SSE, retained hashes and off-topic rejection passed.
- Live traffic was still100% on0045 during these checks. Promotion is now permitted for this validated candidate. Frontend bundle is unchanged.

## Current plan — catalogue integration, 12 September

- **Mode / recipe:** MODIFY, existing FastAPI/Vue applications and separate Python parcours pipeline; retain the existing AZCLI/Container Apps recipe. No new resources, dependencies or infrastructure migration planned.
- **Approval:** integration sequence presented at 15:24; Eneric instructed at 15:25 to execute it autonomously and test each stage. Routine implementation decisions are delegated. External publication, private-data exposure and Azure target confirmation remain separate safety gates.
- **Data:** the newly consolidated private, versioned workbook is the integration candidate, not the currently deployed catalogue. Preserve its original; use explicit input paths and never copy the workbook, private mapping or generated private content into the public repository.
- **Architecture:** existing Azure backend + GitHub Pages frontend. Existing development target is France Central; subscription and resource identity must be reconfirmed through the prescribed Azure workflow before deployment. No change to the official Simplon environment.
- **Stage 1:** update roadmap, changelog, tracking and handoff; distinguish saved workbook, local application changes and deployed versions.
- **Stage 2:** make catalogue-sheet selection explicit and reject malformed/ambiguous inputs; derive missing sector options from indexed metadata while preserving existing choice order and domains without a sector question. Cover with synthetic offline tests.
- **Stage 3:** prepare a safe explicit-source generation path in the existing parcours pipeline; preserve published ID/hash associations and the six-step templates. Do not run the legacy backend generator, rotate the salt, or overwrite existing generated directories.
- **Stage 4:** run targeted regression tests, then an offline in-memory check against the authorized local workbook if needed. Do not persist unprotected content or call external embeddings from this check.
- **Stage 5:** before a real index rebuild, page publication or Azure update, establish the authorized destination and exposure boundary. Confirm the Azure target, run azure-validate, then azure-deploy only if its gates pass. Public GitHub receives reviewed source/documentation only, with exact outbound preview and confirmation.
- **Acceptance:** no data/ID renumbering, no taxonomy redesign, verbatim fields and metadata prefilters preserved; source/index/mapping/pages form one coherent release with an identified rollback. Success of synthetic tests is not full semantic relevance calibration.

### Validation proof — new integration

Local preparation evidence, **not an Azure deployment validation**:

| Check | Command / method | Result |
|---|---|---|
| Backend integration, index safety and generator regressions | Scoped `.venv` Python, `-B -m unittest discover -s tests -q` from `backend` | 182 passed; external parcours repository present. |
| Frontend state and types | `npm run check:chat` and `npm run type-check` | 19 state tests passed; typecheck passed. |
| Real source import | `python -m app.scripts.index_documents --validate-only "<authorized-private-source>"` | Success, no Chroma access or embedding calls. Counts retained privately. |
| Real catalogue compatibility | In-memory import, metadata filters, retained mapping, template rendering and source hash comparison | Entire current catalogue covered; no pages/index written, no model calls. Private evidence in local tracking. |

Python available locally is 3.14; `langchain-core==0.3.15` was restored in an ignored scoped environment after a missing-dependency failure. Existing libraries report a Pydantic-v1/Python-3.14 compatibility warning. These runs do not replace validation in the production Python 3.11 image or a real Chroma/embedding build.

Remaining release gates: confirm target subscription/region, approve the exact outbound code/documentation diff, determine permitted access to new catalogue texts, reconcile historical mapped pages, then build a new private index and run real dev end-to-end checks. Do not reuse the historical proof below to mark this release `Validated`.

### Azure validation checkpoint — not passed

`azure-validate` loaded this plan after preparation. No Azure deployment command or external embedding request was executed: the catalogue's no-publication constraint is not resolved, the target has not been reconfirmed for this release, and no Docker executable is available locally for the production-image check. Recipe overview files referenced by the installed validation skill are absent; the available AZCLI error reference was read. The local tests above pass, but they cannot satisfy these release gates. `azure-deploy` was therefore not invoked.

## Current deployment result

- ACR builds dd2a (initial backend0044), dd2b (frontend0023), dd2c (final backend0045): Succeeded.
- Backend final immutable image: `acravoulia97186.azurecr.io/avoulia-backend@sha256:9408ae9a6d8ffc1275a6b6c03f5bba5bbfbb59120f14d4b20b87c44b06b414ea`, tag `v2-nomatch-20260910-r2`.
- Frontend: `acravoulia97186.azurecr.io/avoulia-frontend:v2-nomatch-20260910`.
- Final revisions Healthy, traffic100 %. First numeric13 edge found on0044, corrected and retested on0045.
- Live mobile390px: input and send fully within viewport; normal guided path13/BTP/objective4, fiscal no-match, clarification back to meeting notes, ranked list, first detail and correct parcours URL, return to objective. Desktop1240px input/send visible.
- Direct non-stream request on0045: approved no-match message, zero IDs, no pending action, original domain/sector/intention retained.
- Two served-page SHA-256 values unchanged from baseline below; data/pages/pitch inherited by construction, not rebuilt from local workbook.
- Final local tests106 backend,19 frontend; build/typecheck success. No exhaustive production relevance or whole-catalog UX claim.

## 7. Validation Proof — historical 10 September deployment only

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
