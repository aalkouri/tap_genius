#!/usr/bin/env bash
# Deploys backend + frontend. Requires: aws cli, sam cli, configured AWS credentials.
set -euo pipefail
cd "$(dirname "$0")/.."
STACK="${STACK:-tap-genius}"
REGION="${AWS_REGION:-us-east-1}"

sam build
sam deploy --stack-name "$STACK" --region "$REGION" --resolve-s3 \
  --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset

out() { aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }
WS_URL=$(out WebSocketUrl); BUCKET=$(out SiteBucketName); DIST=$(out DistributionId); SITE=$(out SiteUrl)

echo "window.TAP_GENIUS_WS = '$WS_URL';" > frontend/config.js
aws s3 sync frontend/ "s3://$BUCKET/" --delete --region "$REGION"
git checkout -- frontend/config.js 2>/dev/null || true   # keep local placeholder in git
aws cloudfront create-invalidation --distribution-id "$DIST" --paths '/*' >/dev/null
echo "Deployed: $SITE"
