#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_FILE="$ROOT_DIR/infra/aws/visitor-counter/template.yaml"
COUNTER_DIR="$ROOT_DIR/infra/aws/visitor-counter"

command -v sam >/dev/null 2>&1 || {
  echo "sam CLI is required." >&2
  exit 1
}

command -v npm >/dev/null 2>&1 || {
  echo "npm is required." >&2
  exit 1
}

: "${AWS_REGION:?Set AWS_REGION.}"
: "${STACK_NAME:?Set STACK_NAME.}"

PROJECT_NAME="${PROJECT_NAME:-pink-hunter}"
ENVIRONMENT_NAME="${ENVIRONMENT_NAME:-staging}"
ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-https://next.pinkhunter.flalaz.com,https://pinkhunter.flalaz.com}"
SITE_COUNTER_KEY="${SITE_COUNTER_KEY:-pinkhunter}"

pushd "$COUNTER_DIR" >/dev/null
npm install --omit=dev
popd >/dev/null

sam build --template-file "$TEMPLATE_FILE"
sam deploy \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    ProjectName="$PROJECT_NAME" \
    EnvironmentName="$ENVIRONMENT_NAME" \
    AllowedOrigins="$ALLOWED_ORIGINS" \
    SiteCounterKey="$SITE_COUNTER_KEY"

aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output table
