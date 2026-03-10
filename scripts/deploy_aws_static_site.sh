#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_FILE="$ROOT_DIR/infra/aws/static-site/template.yaml"

command -v aws >/dev/null 2>&1 || {
  echo "aws CLI is required." >&2
  exit 1
}

: "${AWS_REGION:?Set AWS_REGION.}"
: "${STACK_NAME:?Set STACK_NAME.}"
: "${APP_BUCKET_NAME:?Set APP_BUCKET_NAME.}"
: "${DATA_BUCKET_NAME:?Set DATA_BUCKET_NAME.}"

PROJECT_NAME="${PROJECT_NAME:-pink-hunter}"
ENVIRONMENT_NAME="${ENVIRONMENT_NAME:-staging}"
PRICE_CLASS="${PRICE_CLASS:-PriceClass_100}"
CUSTOM_DOMAIN_NAME="${CUSTOM_DOMAIN_NAME:-}"
ACM_CERTIFICATE_ARN="${ACM_CERTIFICATE_ARN:-}"
HOSTED_ZONE_ID="${HOSTED_ZONE_ID:-}"

aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --template-file "$TEMPLATE_FILE" \
  --parameter-overrides \
    ProjectName="$PROJECT_NAME" \
    EnvironmentName="$ENVIRONMENT_NAME" \
    AppBucketName="$APP_BUCKET_NAME" \
    DataBucketName="$DATA_BUCKET_NAME" \
    PriceClass="$PRICE_CLASS" \
    CustomDomainName="$CUSTOM_DOMAIN_NAME" \
    AcmCertificateArn="$ACM_CERTIFICATE_ARN" \
    HostedZoneId="$HOSTED_ZONE_ID"

aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output table
