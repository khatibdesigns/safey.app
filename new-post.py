#!/usr/bin/env python3
"""Generates a blog post page matching the site template.

Posts were hand-assembled before, which meant the GA4 tag, Snap pixel,
tracker, canonical, schema and footer all had to be copied correctly every
time. This keeps them identical by construction.

    python3 new-post.py post.json
"""
import json, sys, pathlib, html

ROOT = pathlib.Path(__file__).parent

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Safey</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="https://safey.app/blog/{slug}/">
<link rel="alternate" hreflang="en" href="https://safey.app/blog/{slug}/">
<link rel="alternate" hreflang="x-default" href="https://safey.app/blog/{slug}/">
<meta name="keywords" content="{keywords}">
<meta name="theme-color" content="#0c1417">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta}">
<meta property="og:url" content="https://safey.app/blog/{slug}/">
<meta property="og:image" content="https://safey.app/assets/02_dashboard.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://safey.app/assets/02_dashboard.png">
<!-- Google tag (gtag.js) — Safey / SafeSync GA4 property 161462897 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1JGCT9MDZK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-1JGCT9MDZK');</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<!-- Snap Pixel -->
<script type="text/javascript">
(function(e,t,n){{if(e.snaptr)return;var a=e.snaptr=function(){{a.handleRequest?a.handleRequest.apply(a,arguments):a.queue.push(arguments)}};a.queue=[];var s='script';var r=t.createElement(s);r.async=!0;r.src=n;var u=t.getElementsByTagName(s)[0];u.parentNode.insertBefore(r,u)}})(window,document,'https://sc-static.net/scevent.min.js');
snaptr('init','6f2962a7-b994-4523-845c-85ccf9887ef1');
snaptr('track','PAGE_VIEW');
</script>
<!-- End Snap Pixel -->
</head>
<body>
<nav><div class="nav-row">
  <a class="brand" href="/"><span class="mk"><svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z" fill="currentColor"/></svg></span> Safey</a>
  <div class="nav-right">
    <a class="btn-app" href="https://apps.apple.com/app/id1189852939"><span><small>Free on the</small><b>App&nbsp;Store</b></span></a>
  </div>
</div></nav>

<main class="page"><div class="wrap">
  <div class="crumbs"><a href="/">Home</a> › <a href="/blog/">Guides</a> › {crumb}</div>
  <span class="eyebrow">Guide · Privacy</span>
  <h1>{title}</h1>
  <p class="meta">{date} · Safey</p>

  <div class="prose">
{body}
  </div>

  <div class="cta">
    <p><strong>{cta_title}</strong><br>{cta_sub}</p>
    <a class="btn" href="https://apps.apple.com/app/id1189852939">Download Safey — free on the App Store</a>
  </div>

  <div class="faq">
    <h2>FAQ</h2>
{faq_html}
  </div>
</div></main>

<footer><div class="foot-row">
  <div>© 2026 Safey — a private vault by <a href="https://khatibdesigns.com">Khatib Designs</a>.</div>
  <div class="foot-links"><a href="/">Home</a><a href="/blog/">Guides</a><a href="/ar/">العربية</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></div>
</div></footer>
<script src="/assets/track.js" defer></script>
</body>
</html>
"""


def build(cfg):
    slug = cfg["slug"]
    article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": cfg["title"], "description": cfg["meta"],
        "datePublished": cfg["iso"], "dateModified": cfg["iso"],
        "author": {"@type": "Organization", "name": "Safey"},
        "publisher": {"@type": "Organization", "name": "Khatib Designs"},
        "mainEntityOfPage": f"https://safey.app/blog/{slug}/",
        "keywords": cfg["keywords"]}, separators=(",", ":"))
    faq = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in cfg["faq"]]}, separators=(",", ":"))
    faq_html = "\n".join(
        f"    <details><summary>{html.escape(q)}</summary><p>{a}</p></details>"
        for q, a in cfg["faq"])
    page = TEMPLATE.format(article_schema=article, faq_schema=faq,
                           faq_html=faq_html, **cfg)
    out = ROOT / "blog" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page)
    print(f"wrote blog/{slug}/index.html  ({len(cfg['body'].split())} words body)")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        build(json.loads(pathlib.Path(f).read_text()))
