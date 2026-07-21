/* Safey — conversion + drop-off instrumentation.
 *
 * The site had 17 pages of App Store links and no way to tell whether anyone
 * ever tapped one. GA4 could show arrivals and exits but not the one action
 * that matters. This records:
 *
 *   app_store_click  — the conversion. Which page and which link drove it.
 *   scroll_depth     — 25/50/75/100%. Where on a page attention dies.
 *   engaged_15s      — separates a real read from an instant bounce.
 *
 * Defensive throughout: if gtag or snaptr is absent nothing here throws.
 */
(function () {
  "use strict";

  var ga = function (name, params) {
    try { if (typeof gtag === "function") gtag("event", name, params || {}); } catch (e) {}
  };
  var snap = function (name, params) {
    try { if (typeof snaptr === "function") snaptr("track", name, params || {}); } catch (e) {}
  };

  var page = location.pathname || "/";

  // ---- Conversion: any outbound App Store tap -------------------------------
  // Capture phase, so it still fires if something else stops propagation.
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href*="apps.apple.com"]') : null;
    if (!a) return;
    var label = (a.textContent || "").trim().slice(0, 60) || "app-store-link";
    ga("app_store_click", { page_path: page, link_text: label, link_url: a.href });
    // Snap's closest honest standard event for "left for the store".
    snap("CUSTOM_EVENT_1", { description: "app_store_click", page: page });
  }, true);

  // ---- Drop-off: how far down the page they got ------------------------------
  var marks = [25, 50, 75, 100];
  var hit = {};
  var lastCheck = 0;
  function checkScroll() {
    var doc = document.documentElement;
    var scrollable = doc.scrollHeight - window.innerHeight;
    if (scrollable <= 0) return;
    var pct = ((window.pageYOffset || doc.scrollTop) / scrollable) * 100;
    for (var i = 0; i < marks.length; i++) {
      var m = marks[i];
      if (pct >= m && !hit[m]) {
        hit[m] = true;
        ga("scroll_depth", { page_path: page, percent_scrolled: m });
      }
    }
  }
  // Time-based throttle rather than a requestAnimationFrame flag: a rAF that
  // never fires (backgrounded tab) would latch the flag and silently kill
  // scroll tracking for the rest of the session.
  window.addEventListener("scroll", function () {
    var now = Date.now();
    if (now - lastCheck < 200) return;
    lastCheck = now;
    checkScroll();
  }, { passive: true });

  // ---- Engagement: did they actually stay? ----------------------------------
  setTimeout(function () { ga("engaged_15s", { page_path: page }); }, 15000);
})();
