# Preset Embedded Dashboard on GCP Cloud Run

This guide documents how to host a Preset embedded dashboard on Google Cloud Run.

Reference implementation:
- https://github.com/fredchan23/preset-iframe-embed/blob/master/README.md

## Goal

After completing this guide, your embedded Preset dashboard is accessible through a public Cloud Run URL.

## End-to-end flow

1. Host embedded Preset app on Cloud Run.
2. Configure Preset to allow the Cloud Run domain for embedding.
3. Validate that the dashboard loads through the deployed URL.

## Prerequisites

- `gcloud` CLI installed and authenticated.
- GCP project with billing enabled.
- Preset embedded dashboard details:
  - `DASHBOARD_ID`
  - `SUPERSET_DOMAIN`
  - `PRESET_TEAM`
  - `WORKSPACE_SLUG`
- Preset API credentials:
  - `API_TOKEN`
  - `API_SECRET`

## Deploy embedded app to Cloud Run

Run from the embed app repository root (based on the reference implementation):

```bash
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud config set run/region asia-southeast1

gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

printf "%s" "YOUR_API_TOKEN" | gcloud secrets create preset-api-token --data-file=-
printf "%s" "YOUR_API_SECRET" | gcloud secrets create preset-api-secret --data-file=-

gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID \
  --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud run deploy embedded-example \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars DASHBOARD_ID=YOUR_DASHBOARD_ID,SUPERSET_DOMAIN=https://YOUR_SUPERSET_DOMAIN,PRESET_TEAM=YOUR_TEAM_ID,WORKSPACE_SLUG=YOUR_WORKSPACE_SLUG \
  --set-secrets API_TOKEN=preset-api-token:latest,API_SECRET=preset-api-secret:latest
```

Save the deployed HTTPS URL (example: `https://embedded-example-xxxxx.asia-southeast1.run.app`).

## Configure Preset embedding domain

In Preset Manager:

1. Open the embedded dashboard settings.
2. Add your Cloud Run domain to allowed embedding domains.
3. Verify the dashboard loads from the Cloud Run URL.

## Operational checklist

- If Cloud Run URL changes, update any downstream references that link to it.
- If embedding fails, re-check Preset allowed domains and Cloud Run service status.
- Rotate API credentials in Secret Manager as needed.

## Troubleshooting quick notes

- `HTTP 503` on Cloud Run: inspect Cloud Run revision logs.
- Secret permission errors: verify `roles/secretmanager.secretAccessor` on the runtime service account.
- Dashboard not loading in iframe: ensure `SUPERSET_DOMAIN` includes `https://` and embedding domain is allowed in Preset.
