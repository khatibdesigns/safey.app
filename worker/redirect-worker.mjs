/**
 * safey.app edge redirect + server-side GA4 count.
 *
 * Behaviour is identical to the Cloudflare redirect rule it replaces:
 *   any query param  ->  302 to the App Store
 *   no params        ->  the real site (pass through to origin)
 *   ?stay=1          ->  the real site (escape hatch)
 *   crawlers         ->  the real site (ad reviewers / Googlebot)
 *
 * The only addition is a GA4 Measurement Protocol event fired on the redirect.
 * It runs in ctx.waitUntil(), so it happens AFTER the 302 is already sent —
 * zero added latency, and its failure can never affect the redirect or the user.
 *
 * Fail-open: any unexpected error falls through to the origin, so the site can
 * never be taken down by this Worker.
 */
const APP_STORE = "https://apps.apple.com/app/id1189852939";
const CRAWLER = /bot|crawler|spider|Googlebot|AdsBot|facebookexternalhit|Applebot|mediapartners|lighthouse|headless/i;

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);
      const ua = request.headers.get("user-agent") || "";
      const hasParams = url.search.length > 1;          // "?a=b"
      const isStay = url.search.includes("stay=1");     // escape hatch
      const isCrawler = CRAWLER.test(ua);

      if (hasParams && !isStay && !isCrawler) {
        ctx.waitUntil(pingGA4(request, url, env));       // background, non-blocking
        return Response.redirect(APP_STORE, 302);
      }
      return fetch(request);                             // pass through to the site
    } catch (e) {
      return fetch(request);                             // never break the site
    }
  },
};

async function pingGA4(request, url, env) {
  try {
    if (!env.GA4_MEASUREMENT_ID || !env.GA4_API_SECRET) return;
    // Reuse the visitor's _ga client id if present, else mint one.
    const cookie = request.headers.get("cookie") || "";
    const m = cookie.match(/_ga=GA\d\.\d\.(\d+\.\d+)/);
    const clientId = m ? m[1] : crypto.randomUUID();
    const p = url.searchParams;
    const body = JSON.stringify({
      client_id: clientId,
      events: [{
        name: "redirect_to_store",
        params: {
          page_location: url.href,
          page_path: url.pathname,
          source: p.get("utm_source") || "",
          medium: p.get("utm_medium") || "",
          campaign: p.get("utm_campaign") || "",
          session_id: Date.now().toString(),
          engagement_time_msec: 1,
        },
      }],
    });
    const endpoint =
      `https://www.google-analytics.com/mp/collect?measurement_id=${env.GA4_MEASUREMENT_ID}&api_secret=${env.GA4_API_SECRET}`;
    await fetch(endpoint, { method: "POST", body });
  } catch (e) { /* never throws into the response path */ }
}
