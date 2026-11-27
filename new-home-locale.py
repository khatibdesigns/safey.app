#!/usr/bin/env python3
"""Build every homepage (/, /ar/, /es/, /pt/, /fr/, /de/, /it/, /tr/, /id/) from one template.

Text lives in locales/<lang>.json (en.json is the source; the others mirror its keys).
Styles live in assets/home.css. Edit those, then run:

    python3 new-home-locale.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).parent
STORE = "https://apps.apple.com/app/id1189852939"
PLAY = "https://play.google.com/store/apps/details?id=com.khatibdesigns.safey"
ALL = {"en": ("/", "English"), "ar": ("/ar/", "العربية"), "es": ("/es/", "Español"),
       "pt": ("/pt/", "Português"), "fr": ("/fr/", "Français"), "de": ("/de/", "Deutsch"),
       "it": ("/it/", "Italiano"), "tr": ("/tr/", "Türkçe"), "id": ("/id/", "Bahasa Indonesia")}

GUIDES = [  # English guides, linked from every non-Arabic page as crawl paths
    ("free-up-storage-iphone", "How to Free Up Storage on iPhone Without Deleting Photos"),
    ("icloud-storage-full-alternatives", "iCloud Storage Full? Free Up Space Without Paying"),
    ("safey-vs-keepsafe", "Safey vs KeepSafe: The Best Free Photo Vault Alternative"),
    ("best-photo-vault-apps-iphone", "The Best Photo Vault Apps for iPhone"),
    ("app-lock-iphone", "App Lock for iPhone (and What It Can't Protect)"),
    ("hide-photos-iphone", "How to Hide Photos on iPhone"),
    ("decoy-passcode-iphone", "Decoy Passcode: Open an Empty Vault Under Pressure"),
    ("break-in-alerts-photo-vault", "How to Know If Someone Tried to Open Your Phone"),
]
AR_GUIDES = ["free-up-storage-iphone", "icloud-storage-full-alternatives", "safey-vs-keepsafe",
             "is-the-hidden-album-really-hidden", "app-lock-iphone", "decoy-passcode-iphone",
             "break-in-alerts-photo-vault", "safey-vs-private-photo-vault"]

SHIELD = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" fill="currentColor"/></svg>'
APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.1-2.8.9-3.5.9-.7 0-1.8-.8-3-.8-1.5 0-3 .9-3.8 2.3-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3 1.2 0 1.6-.7 3-.7s1.8.7 3 .7c1.3 0 2.1-1.1 2.8-2.3.9-1.3 1.3-2.6 1.3-2.6s-2.5-1-2.5-3.8zM14.2 5.8c.6-.8 1.1-1.9 1-3-.9 0-2.1.6-2.7 1.4-.6.7-1.1 1.8-1 2.9 1 .1 2.1-.5 2.7-1.3z"/></svg>'
PLAYI = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3.2v17.6c0 .4.4.7.8.5L19.6 13a1.1 1.1 0 000-2L4.8 2.7c-.4-.2-.8.1-.8.5z" fill="currentColor"/></svg>'
S = 'stroke="currentColor" stroke-width="1.8"'
ICON = {
    "photo": f'<svg viewBox="0 0 24 24" fill="none"><rect x="3.5" y="5" width="17" height="14" rx="2.5" {S}/><circle cx="9" cy="10" r="1.6" fill="currentColor"/><path d="M4.5 17l5-4.5 3 2.5 3.5-3.5 3.5 3.5" {S} stroke-linejoin="round"/></svg>',
    "key": f'<svg viewBox="0 0 24 24" fill="none"><circle cx="8" cy="12" r="4" {S}/><path d="M12 12h9M18 12v3M21 12v2" {S} stroke-linecap="round"/></svg>',
    "card": f'<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="6" width="18" height="12" rx="2.5" {S}/><path d="M3 10h18" {S}/></svg>',
    "note": f'<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="3.5" width="14" height="17" rx="2.5" {S}/><path d="M9 9h6M9 13h6M9 17h3" {S} stroke-linecap="round"/></svg>',
    "file": f'<svg viewBox="0 0 24 24" fill="none"><path d="M6 3.5h7l5 5V20a.5.5 0 01-.5.5h-11A.5.5 0 016 20V3.5z" {S}/><path d="M13 3.5v5h5" {S}/></svg>',
    "face": '<svg viewBox="0 0 24 24" fill="none"><path d="M4 8V6a2 2 0 012-2h2M16 4h2a2 2 0 012 2v2M20 16v2a2 2 0 01-2 2h-2M8 20H6a2 2 0 01-2-2v-2M9 9.5v1M15 9.5v1M12 9.5v3.5h-1M9.5 16c1.4 1 3.6 1 5 0" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    "lock": f'<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="9" rx="2" {S}/><path d="M8 11V8a4 4 0 018 0v3" {S}/></svg>',
    "clock": f'<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8.5" {S}/><path d="M12 7.5V12l3 2" {S} stroke-linecap="round"/></svg>',
    "cam": f'<svg viewBox="0 0 24 24" fill="none"><path d="M4 8.5A1.5 1.5 0 015.5 7h2l1.5-2h6l1.5 2h2A1.5 1.5 0 0120 8.5v9a1.5 1.5 0 01-1.5 1.5h-13A1.5 1.5 0 014 17.5v-9z" {S}/><circle cx="12" cy="13" r="3.2" {S}/></svg>',
    "dots": f'<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="3" {S}/><path d="M8 12h.01M12 12h.01M16 12h.01" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>',
}
VAULT_ICONS = [("photo", "var(--photos)"), ("key", "var(--apps)"), ("card", "var(--msg)"), ("note", "#FF9500"), ("file", "var(--sys)")]
PRIV_ICONS = [("face", "var(--green)"), ("lock", "var(--vault)"), ("key", "var(--apps)"), ("clock", "var(--sys)"), ("cam", "#FF3B30"), ("dots", "#FF9500")]
STEP_COLORS = ['--c:var(--vault)', '--c:var(--photos);color:var(--ink)', '--c:var(--green)']
LEGEND = ["var(--photos)", "var(--apps)", "var(--msg)", "var(--sys)", "var(--other)"]
BAR = '<i id="seg" style="flex-basis:52%;background:var(--photos)"></i><i style="flex-basis:18%;background:var(--apps)"></i><i style="flex-basis:9%;background:var(--msg)"></i><i style="flex-basis:12%;background:var(--sys)"></i><i style="flex-basis:5.5%;background:var(--other)"></i>'
MINI = '<i style="flex-basis:14%;background:var(--photos)"></i><i style="flex-basis:18%;background:var(--apps)"></i><i style="flex-basis:9%;background:var(--msg)"></i><i style="flex-basis:12%;background:var(--sys)"></i><i style="flex-basis:47%;background:var(--line)"></i>'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def rich(s):
    """Escape text but keep the <b>…</b> emphasis the locale files use."""
    return esc(s).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


def store_btns(t):
    return (f'<a class="btn btn-store" href="{STORE}" rel="noopener">{APPLE}<span><small>{esc(t["store_small"])}</small><span class="big">App Store</span></span></a>\n'
            f'        <a class="btn btn-store" href="{PLAY}" rel="noopener">{PLAYI}<span><small>{esc(t["play_small"])}</small><span class="big">Google Play</span></span></a>')


def guides(lang):
    if lang == "ar":
        items = [(f"/ar/blog/{g}/", json.loads((ROOT / "ar-posts" / f"{g}.json").read_text())["title"], "") for g in AR_GUIDES]
        return items, "/ar/blog/"
    attr = "" if lang == "en" else ' lang="en"'
    return [(f"/blog/{g}/", x, attr) for g, x in GUIDES], "/blog/"


def head(t, lang):
    url = "https://safey.app" + ALL[lang][0]
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="https://safey.app{p}">' for l, (p, _) in ALL.items())
    return f"""<!doctype html>
<html lang="{lang}"{' dir="rtl"' if lang == "ar" else ""}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t["title"])}</title>
<meta name="description" content="{esc(t["desc"])}">
<link rel="canonical" href="{url}">
{alts}
<link rel="alternate" hreflang="x-default" href="https://safey.app/">
<meta name="keywords" content="{esc(t["keywords"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#F2F2F7">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Safey">
<meta property="og:locale" content="{t["og_locale"]}">
<meta property="og:title" content="{esc(t["title"])}">
<meta property="og:description" content="{esc(t["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://safey.app/assets/02_dashboard.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(t["title"])}">
<meta name="twitter:description" content="{esc(t["desc"])}">
<meta name="twitter:image" content="https://safey.app/assets/02_dashboard.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-itunes-app" content="app-id=1189852939">
<!-- Google tag (gtag.js) — Safey / SafeSync GA4 property 161462897 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1JGCT9MDZK"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-1JGCT9MDZK');
</script>
<link rel="stylesheet" href="/assets/home.css">
<!-- Snap Pixel -->
<script type="text/javascript">
(function(e,t,n){{if(e.snaptr)return;var a=e.snaptr=function(){{a.handleRequest?a.handleRequest.apply(a,arguments):a.queue.push(arguments)}};a.queue=[];var s='script';var r=t.createElement(s);r.async=!0;r.src=n;var u=t.getElementsByTagName(s)[0];u.parentNode.insertBefore(r,u)}})(window,document,'https://sc-static.net/scevent.min.js');
snaptr('init','6f2962a7-b994-4523-845c-85ccf9887ef1');
snaptr('track','PAGE_VIEW');
</script>
<!-- End Snap Pixel -->
</head>"""


def body(t, lang):
    home = ALL[lang][0]
    other = ("ar", "/ar/", "العربية") if lang != "ar" else ("en", "/", "English")
    legend = "".join(f'<li style="--c:{c}">{esc(x)}</li>' for c, x in zip(LEGEND, t["legend"]))
    secline = "".join(f"<span>{rich(x)}</span>" for x in t["secline"])
    steps = "\n        ".join(f'<li><span class="n" style="{c}">{i}</span><h3>{esc(h)}</h3><p>{esc(p)}</p></li>'
                             for i, (c, (h, p)) in enumerate(zip(STEP_COLORS, t["steps"]), 1))
    vault = "\n          ".join(f'<li><span class="t" style="--c:{c}">{ICON[k]}</span><span class="tx"><b>{esc(h)}</b><small>{esc(s)}</small></span></li>'
                                 for (k, c), (h, s) in zip(VAULT_ICONS, t["vault_rows"]))
    priv = "\n        ".join(
        f'<li><span class="t" style="--c:{c}">{ICON[k]}</span><span class="tx"><b>{esc(h)}</b>{f"<small>{esc(s)}</small>" if s else ""}</span>'
        f'<span class="v{" pro" if v == "PRO" else ""}">{esc(v)}</span></li>'
        for (k, c), (h, s, v) in zip(PRIV_ICONS, t["priv_rows"]))
    tiers = "\n        ".join(
        f'<div class="tier{" pop" if n == 1 else ""}"><span class="tag">{esc(tag)}</span><div class="amt">{esc(amt)}</div><div class="per">{esc(per)}</div>'
        f'<div class="cap"><i style="width:{w}"></i></div><p>{esc(p)}</p><span class="pill">{esc(pill)}</span></div>'
        for n, (w, (tag, amt, per, p, pill)) in enumerate(zip(["2%", "25%", "100%"], t["tiers"])))
    faqs = "\n        ".join(f'<details{" open" if n == 0 else ""}><summary>{esc(q)}</summary><div class="body">{esc(a)}</div></details>'
                             for n, (q, a) in enumerate(t["faqs"]))
    glist, gall = guides(lang)
    gl = "\n        ".join(f'<a href="{u}"{a}>{esc(x)}</a>' for u, x, a in glist)
    langs = "\n      ".join(f'<a href="{p}" hreflang="{l}" lang="{l}">{n}</a>' for l, (p, n) in ALL.items() if l != lang)
    gpre = "/ar" if lang == "ar" else ""
    return f"""
<body>
<nav id="nav">
  <div class="wrap nav-row">
    <a class="brand" href="{home}"><span class="mk">{SHIELD}</span>Safey</a>
    <div class="nav-links">
      <a href="#how">{esc(t["nav_how"])}</a>
      <a href="#pricing">{esc(t["nav_pricing"])}</a>
      <a href="{gall}">{esc(t["nav_guides"])}</a>
      <a class="lang" href="{other[1]}" lang="{other[0]}">{other[2]}</a>
    </div>
    <a class="btn btn-blue nav-cta" href="{STORE}" rel="noopener"><span class="big">{esc(t["nav_cta"])}</span></a>
  </div>
</nav>

<main>
  <header class="hero">
    <div class="wrap">
      <div class="hero-top">
        <h1>{esc(t["h1_before"])}<mark>{esc(t["h1_mark"])}</mark>{esc(t["h1_after"])}</h1>
        <div>
          <p class="lede">{esc(t["lede"])}</p>
          <div class="ctas">
        {store_btns(t)}
          </div>
          <a class="how-link" href="#how">{esc(t["how_link"])}</a>
        </div>
      </div>

      <div class="panel" id="panel" aria-label="{esc(t["panel_label"])}" data-before="{esc(t["used_before"])}" data-after="{esc(t["used_after"])}" data-saved="{esc(t["saved"])}" data-phone="{esc(t["device_phone"])}">
        <div class="ph"><b id="device">{esc(t["device_iphone"])}</b><span id="used">{esc(t["used_before"])}</span></div>
        <div class="bar" aria-hidden="true">{BAR}</div>
        <ul class="legend">{legend}</ul>
        <div class="row">
          <span class="ico" aria-hidden="true">{SHIELD}</span>
          <label for="sw"><b>{esc(t["toggle_title"])}</b><small>{esc(t["toggle_sub"])}</small></label>
          <input type="checkbox" class="sw" id="sw" role="switch">
        </div>
        <p class="saved" id="saved" aria-live="polite"></p>
        <div class="secline">{secline}</div>
        <p class="note">{esc(t["example_note"])}</p>
      </div>
    </div>
  </header>

  <section id="how">
    <div class="wrap">
      <div class="sh"><span class="kick">{esc(t["steps_kick"])}</span><h2>{esc(t["steps_h2"])}</h2></div>
      <ol class="steps">
        {steps}
      </ol>
      <p class="fine">{esc(t["steps_fine"])} <a href="#pricing">{esc(t["see_plans"])}</a></p>
    </div>
  </section>

  <section>
    <div class="wrap split">
      <div>
        <div class="sh"><span class="kick">{esc(t["vault_kick"])}</span><h2>{esc(t["vault_h2"])}</h2><p>{esc(t["vault_p"])}</p></div>
        <ul class="group">
          {vault}
        </ul>
      </div>
      <div class="phone"><img src="/assets/02_dashboard.png" alt="{esc(t["dashboard_alt"])}" width="292" height="610" loading="lazy"></div>
    </div>
  </section>

  <section>
    <div class="wrap split">
      <div class="sh" style="margin:0"><span class="kick">{esc(t["priv_kick"])}</span><h2>{esc(t["priv_h2"])}</h2><p>{esc(t["priv_p"])}</p>
        <p class="honest">{esc(t["priv_honest"])}</p></div>
      <ul class="group">
        {priv}
      </ul>
    </div>
  </section>

  <section id="pricing">
    <div class="wrap">
      <div class="sh"><span class="kick">{esc(t["price_kick"])}</span><h2>{esc(t["price_h2"])}</h2><p>{esc(t["price_p"])}</p></div>
      <div class="tiers">
        {tiers}
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="sh"><span class="kick">{esc(t["faq_kick"])}</span><h2>{esc(t["faq_h2"])}</h2></div>
      <div class="faq">
        {faqs}
      </div>
    </div>
  </section>

  <section class="guides">
    <div class="wrap">
      <div class="sh"><span class="kick">{esc(t["guides_kick"])}</span><h2>{esc(t["guides_h2"])}</h2></div>
      <div class="guide-grid">
        {gl}
      </div>
      <a class="all" href="{gall}">{esc(t["all_guides"])}</a>
    </div>
  </section>

  <section class="final">
    <div class="wrap"><div class="final-card">
      <div>
        <h2>{esc(t["final_h2"])}</h2>
        <p>{esc(t["final_p"])}</p>
        <div class="mini" aria-hidden="true">{MINI}</div>
      </div>
      <div class="ctas">
        {store_btns(t)}
      </div>
    </div></div>
  </section>
</main>

<footer>
  <div class="wrap foot-row">
    <div>© 2026 Safey, {esc(t["foot_by"])} <a href="https://khatibdesigns.com">Khatib Designs</a>.</div>
    <div class="foot-links">
      <a href="{STORE}">App Store</a>
      <a href="{PLAY}">Google Play</a>
      <a href="https://instagram.com/safey.app" rel="me">Instagram</a>
      <a href="{gpre}/blog/">{esc(t["foot_guides"])}</a>
      <a href="{gpre}/privacy/">{esc(t["foot_privacy"])}</a>
      <a href="{gpre}/terms/">{esc(t["foot_terms"])}</a>
    </div>
    <div class="foot-links">
      {langs}
    </div>
  </div>
</footer>
"""


def schema(t, lang):
    url = "https://safey.app" + ALL[lang][0]
    app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Safey",
           "operatingSystem": "iOS, Android", "applicationCategory": "UtilitiesApplication", "inLanguage": lang,
           "description": t["desc"], "url": url, "downloadUrl": [STORE, PLAY],
           "publisher": {"@type": "Organization", "name": "Khatib Designs", "url": "https://khatibdesigns.com"},
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang,
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faqs"]]}
    return (f'<script type="application/ld+json">\n{json.dumps(app, ensure_ascii=False)}\n</script>\n'
            f'<script type="application/ld+json">\n{json.dumps(faq, ensure_ascii=False)}\n</script>')


SCRIPT = """<script>
(function(){
  var nav = document.getElementById('nav');
  var onScroll = function(){ nav.classList.toggle('stuck', scrollY > 8); };
  onScroll(); addEventListener('scroll', onScroll, {passive:true});

  // The storage demo: flipping the switch shrinks the yellow Photos segment.
  var p = document.getElementById('panel'), sw = document.getElementById('sw'), seg = document.getElementById('seg'),
      used = document.getElementById('used'), saved = document.getElementById('saved'), d = p.dataset;
  if (/Android/i.test(navigator.userAgent)) document.getElementById('device').textContent = d.phone;
  function set(){
    seg.style.flexBasis = sw.checked ? '14%' : '52%';
    used.textContent = sw.checked ? d.after : d.before;
    saved.innerHTML = '';
    if (sw.checked) { var b = document.createElement('b'); b.textContent = '+ ' + d.saved; saved.appendChild(b); }
  }
  sw.addEventListener('change', set);
  // Play it once when the panel comes into view, unless the visitor already touched it.
  var touched = false; sw.addEventListener('pointerdown', function(){ touched = true; });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(e){
      if (e[0].isIntersecting) { io.disconnect(); setTimeout(function(){ if(!touched){ sw.checked = true; set(); } }, 900); }
    }, {threshold:.35});
    io.observe(p);
  }
})();
</script>
<script src="/assets/track.js" defer></script>
<script>/* Android visitors: the header button goes to Google Play. *//Android/i.test(navigator.userAgent)&&document.querySelectorAll('.nav-cta').forEach(function(a){a.href='"""+PLAY+"""'})</script>
</body>
</html>
"""


def build(lang):
    t = json.loads((ROOT / "locales" / f"{lang}.json").read_text())
    html = head(t, lang) + body(t, lang) + "\n" + schema(t, lang) + "\n\n" + SCRIPT
    out = ROOT / ALL[lang][0].strip("/") / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    return out


if __name__ == "__main__":
    for lang in ALL:
        if (ROOT / "locales" / f"{lang}.json").exists():
            print("wrote", build(lang))
