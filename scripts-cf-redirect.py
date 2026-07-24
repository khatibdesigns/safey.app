import os, json, urllib.request, urllib.error
T = os.environ['CF_API_TOKEN']
ZONE = '0896a37e1c85858ef39dece7bdbb846c'   # safey.app

def cf(m, p, b=None):
    r = urllib.request.Request('https://api.cloudflare.com/client/v4' + p,
        data=json.dumps(b).encode() if b else None, method=m,
        headers={'Authorization': f'Bearer {T}', 'Content-Type': 'application/json'})
    try: return json.loads(urllib.request.urlopen(r, timeout=30).read())
    except urllib.error.HTTPError as e: return json.loads(e.read())

# Paid iOS traffic only. Crawlers are excluded so ad reviewers and Googlebot
# still see the real page — Snap already rejected one ad, and a landing page
# that bounces the reviewer invites more of that.
EXPR = ('(http.host eq "safey.app") and '
        '(http.user_agent contains "iPhone" or http.user_agent contains "iPad") and '
        'not (http.user_agent contains "bot" or http.user_agent contains "Bot" or '
        'http.user_agent contains "crawler" or http.user_agent contains "Googlebot" or '
        'http.user_agent contains "AdsBot" or http.user_agent contains "facebookexternalhit") and '
        'not (http.request.uri.query contains "stay=1") and '
        '(http.request.uri.query contains "fbclid" or '
        'http.request.uri.query contains "ttclid" or '
        'http.request.uri.query contains "gclid" or '
        'http.request.uri.query contains "ScCid" or '
        'http.request.uri.query contains "utm_medium=paid_social" or '
        'http.request.uri.query contains "utm_medium=cpc" or '
        'http.request.uri.query contains "utm_medium=paid")')

rule = {
    "description": "Paid iOS traffic to App Store",
    "expression": EXPR,
    "action": "redirect",
    "action_parameters": {"from_value": {
        "status_code": 302,
        "target_url": {"value": "https://apps.apple.com/app/id1189852939"},
        "preserve_query_string": False}}
}

# http_request_dynamic_redirect is the phase that owns Single Redirect rules
r = cf('GET', f'/zones/{ZONE}/rulesets/phases/http_request_dynamic_redirect/entrypoint')
if r.get('success'):
    rs = r['result']
    existing = [x for x in rs.get('rules', []) if x['description'] == rule['description']]
    rules = [x for x in rs.get('rules', []) if x['description'] != rule['description']] + [rule]
    out = cf('PUT', f"/zones/{ZONE}/rulesets/{rs['id']}", {"rules": rules})
    print(('updated' if existing else 'added') + ' rule ->', out.get('success'))
else:
    out = cf('PUT', f'/zones/{ZONE}/rulesets/phases/http_request_dynamic_redirect/entrypoint',
             {"rules": [rule]})
    print('created ruleset ->', out.get('success'))

if not out.get('success'):
    print(json.dumps(out.get('errors'), indent=1)[:600])
else:
    for x in out['result'].get('rules', []):
        print(f"  [{'ON ' if x.get('enabled', True) else 'OFF'}] {x['description']}")
