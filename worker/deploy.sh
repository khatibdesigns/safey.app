#!/usr/bin/env bash
# Redeploy the safey.app edge redirect Worker.
# Reads Cloudflare token from ~/.safey/cf.env and the GA4 MP secret from
# ~/.safey/ga4-mp.env — nothing sensitive lives in this repo.
set -euo pipefail
set -a; . "$HOME/.safey/cf.env"; . "$HOME/.safey/ga4-mp.env"; set +a
AID=40b7f0f5b5a333bb15fa5fd76f722653
cd "$(dirname "$0")"
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$AID/workers/scripts/safey-redirect" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -F "metadata={\"main_module\":\"redirect-worker.mjs\",\"bindings\":[{\"type\":\"plain_text\",\"name\":\"GA4_MEASUREMENT_ID\",\"text\":\"$GA4_MEASUREMENT_ID\"},{\"type\":\"secret_text\",\"name\":\"GA4_API_SECRET\",\"text\":\"$GA4_MP_SECRET\"}],\"compatibility_date\":\"2024-11-01\"};type=application/json" \
  -F "redirect-worker.mjs=@redirect-worker.mjs;type=application/javascript+module" \
  | python3 -c "import sys,json;r=json.load(sys.stdin);print('deploy ->',r.get('success') or r.get('errors'))"
