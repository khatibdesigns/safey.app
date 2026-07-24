/* Safey — send paid traffic straight to the App Store.
 *
 * Someone who clicked an app-install ad has already decided; making them read
 * a landing page first only adds a step to drop off at. Organic visitors still
 * get the site, because they arrived to evaluate, not to install.
 *
 * Deliberately narrow. It only redirects when ALL of these hold:
 *   - the URL carries an ad click id or a paid utm_medium
 *   - the device can actually install the app (iOS only)
 *   - the visitor isn't a crawler (ad reviewers and Googlebot must see the page)
 *   - it hasn't already bounced this session
 *
 * Escape hatch: append ?stay=1 to any URL to view the site normally.
 *
 * Loaded synchronously in <head> on purpose — deferring it would show a flash
 * of the page before the jump.
 */
(function () {
  "use strict";

  var APP_STORE = "https://apps.apple.com/app/id1189852939";
  var params = new URLSearchParams(location.search);

  // Manual override, and a hard stop for anything that looks automated.
  if (params.get("stay") === "1") return;
  var ua = navigator.userAgent || "";
  if (/bot|crawler|spider|crawling|facebookexternalhit|preview|headless|lighthouse|gtmetrix|pingdom|snapchat.*bot|adsbot|mediapartners/i.test(ua)) return;

  // iOS only — Safey has no Android build, so redirecting anyone else sends
  // them to a page they cannot act on.
  var isIOS = /iPad|iPhone|iPod/.test(ua) ||
              (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  if (!isIOS) return;

  // Did this visit come from an ad?
  var CLICK_IDS = ["gclid", "fbclid", "ttclid", "ScCid", "sccid", "msclkid", "twclid", "igshid", "wbraid", "gbraid"];
  var PAID_MEDIUM = /^(cpc|ppc|paid|paidsocial|paid_social|cpm|cpv|display|banner)$/i;
  var hasClickId = CLICK_IDS.some(function (k) { return params.has(k); });
  var medium = params.get("utm_medium") || "";
  var isPaid = hasClickId || PAID_MEDIUM.test(medium);
  if (!isPaid) return;

  // One bounce per session, so a back-button press doesn't trap the visitor.
  try {
    if (sessionStorage.getItem("safey_redirected")) return;
    sessionStorage.setItem("safey_redirected", "1");
  } catch (e) { /* private mode — proceed anyway */ }

  // Carry the campaign into App Store Connect's analytics.
  // NOTE: ct only reports if pt (your App Analytics provider token) is set too.
  var dest = APP_STORE + "?mt=8";
  var campaign = params.get("utm_campaign") || params.get("utm_source");
  if (campaign) dest += "&ct=" + encodeURIComponent(campaign.slice(0, 40));

  // Leave only once GA4 confirms the hit went out.
  //
  // A fixed delay does not work here: measured on the live site, gtag.js only
  // finishes loading at ~342ms and the first hit leaves at ~686ms, so anything
  // shorter drops the event and undercounts exactly the traffic being paid for.
  // event_callback is GA4's own "fire, then navigate" hook, and event_timeout
  // caps the wait when the network is slow. The outer timer is the backstop for
  // gtag.js never arriving at all (blocked, offline), where no callback comes.
  var jumped = false;
  function go() {
    if (jumped) return;
    jumped = true;
    location.replace(dest);
  }

  try {
    if (typeof snaptr === "function") snaptr("track", "APP_INSTALL");
    if (typeof gtag === "function") {
      gtag("event", "ad_redirect_to_store", {
        page_path: location.pathname,
        utm_source: params.get("utm_source") || "",
        utm_campaign: campaign || "",
        transport_type: "beacon",
        event_callback: go,
        event_timeout: 1200
      });
    }
  } catch (e) {}

  setTimeout(go, 1500);
})();
