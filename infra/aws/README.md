# AWS Staging Runbook

This folder contains the AWS implementation for the Pink Hunter staging / production path.

## Components
- `static-site/template.yaml`
  - `S3 + CloudFront`
  - App files and `/data/*` served from separate S3 buckets
  - HTML short cache, assets long cache, GeoJSON medium cache
- `visitor-counter/template.yaml`
  - `API Gateway + Lambda + DynamoDB`
  - `GET /api/v1/visitor-count`
  - `POST /api/v1/visitor-count/hit`
- `visitor-counter/src/index.mjs`
  - Browser-profile visitor dedupe with DynamoDB conditional writes

## Deploy order
1. Deploy the visitor counter stack.
2. Deploy the static site stack.
3. Build the frontend with staging or production env vars.
4. Publish `dist/` to the app bucket and `public/data/` to the data bucket.
5. Create a CloudFront invalidation.
6. Point `next.pinkhunter.flalaz.com` or `pinkhunter.flalaz.com` to the distribution when ready.

## Example env files
- `.env.staging.example`
- `.env.production.example`

## Scripts
- `scripts/deploy_aws_visitor_counter.sh`
- `scripts/deploy_aws_static_site.sh`
- `scripts/publish_to_aws.sh`
- `scripts/smoke_check_deployment.py`

## Notes
- `Mapbox` token allowlist should include `https://next.pinkhunter.flalaz.com/*`, `https://pinkhunter.flalaz.com/*`, and local dev.
- `CloudFront` invalidation should include at least `/`, `/index.html`, `/assets/*`, and `/data/*`.
- `public/data/meta.v2.json` now carries `regions[].coverage_path`, which is what the staging/prod frontend uses for lazy coverage loading.
