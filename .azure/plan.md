# Azure Deployment Plan

## Status

Deployed (revalidated 2026-08-26)

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
