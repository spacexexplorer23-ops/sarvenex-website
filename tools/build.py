# -*- coding: utf-8 -*-
"""Generate sarvenex.com pages from content + JSON data.

    python tools/build.py

Writes: index.html, bn/index.html, privacy.html, sitemap.xml, robots.txt
Sources: tools/content.py, assets/data/products.json, assets/data/projects.json,
         tools/privacy_body.html
Only the Python standard library is used.
"""
import json, os, datetime
from html import escape
from urllib.parse import quote
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from content import SITE, T  # noqa: E402

def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)

PRODUCTS = load("assets/data/products.json")
PROJECTS = load("assets/data/projects.json")
TODAY = datetime.date.today().isoformat()
D = SITE["domain"]

def e(s):
    return escape(str(s or ""), quote=True)

def wa_link(text):
    return f"https://wa.me/{SITE['whatsapp']}?text={quote(text)}"

def loc(obj, lang):
    """Pick the language from {"en":..,"bn":..}; fall back to English."""
    if isinstance(obj, dict):
        return obj.get(lang) or obj.get("en") or ""
    return obj or ""

# ---------------------------------------------------------------- pieces
def head(t, path, extra_ld):
    lang = t["lang"]
    canonical = D + path
    fonts = "family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Hanken+Grotesk:wght@400;500;600"
    if lang == "bn":
        fonts += "&family=Hind+Siliguri:wght@400;500;600;700"
    ld = json.dumps(extra_ld, ensure_ascii=False, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#08111f">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['description'])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{D}/">
<link rel="alternate" hreflang="bn" href="{D}/bn/">
<link rel="alternate" hreflang="x-default" href="{D}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sarvenex">
<meta property="og:title" content="{e(t['og_title'])}">
<meta property="og:description" content="{e(t['description'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{D}/assets/img/og-image.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{'bn_IN' if lang == 'bn' else 'en_IN'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/styles.css">
<link rel="icon" href="/assets/img/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon.png">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<script type="application/ld+json">{ld}</script>
</head>"""

def header(t, home):
    nav = "".join(f'<a href="{home}{h}">{e(l)}</a>' for h, l in t["nav"])
    return f"""<body id="top">
<a class="skip" href="#main">Skip to content</a>
<header class="header"><div class="wrap nav">
<a class="brand" href="{t['dir']}" aria-label="Sarvenex home"><img class="light-logo" src="/assets/img/logo-light.webp" alt="Sarvenex" width="181" height="30"><img class="dark-logo" src="/assets/img/logo-dark.webp" alt="Sarvenex" width="176" height="30"></a>
<nav class="links" id="links" aria-label="Primary">{nav}</nav>
<div class="tools"><a class="lang" href="{t['other_href']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{e(t['other_label'])}</a><button class="icon-btn" id="themeToggle" type="button" aria-label="{e(t['theme'])}"><span id="themeIcon">☾</span></button><a class="btn sm" href="{home}#contact">{e(t['cta'])}</a><button class="icon-btn menu" id="menuBtn" type="button" aria-label="{e(t['menu'])}" aria-expanded="false">☰</button></div>
</div></header>"""

def hero(t):
    term = "".join(f"<div>{line}</div>" for line, _ in t["term"])
    trust = "".join(f"<li>{e(x)}</li>" for x in t["trust"])
    return f"""<section class="hero"><div class="wrap hero-grid">
<div><p class="eyebrow">{e(t['eyebrow'])}</p><h1>{t['h1']}</h1>
<p class="lead">{e(t['lead'])}</p>
<div class="row"><a class="btn" href="#contact">{e(t['cta'])}</a><a class="btn ghost" href="#products">{e(t['hero_btn2'])}</a></div>
<a class="wa-inline" href="{wa_link(t['wa_msg'])}" target="_blank" rel="noopener">{e(t['hero_wa'])} →</a></div>
<div class="term" aria-hidden="true"><div class="term-bar"><b></b><b></b><b></b><span>{e(t['term_title'])}</span></div>
<div class="term-body">{term}</div></div>
</div>
<div class="wrap"><ul class="trust">{trust}</ul></div></section>"""

def product_card(p, t):
    lang = t["lang"]
    st = p.get("status", "soon")
    url = (p.get("url_bn") if lang == "bn" and p.get("url_bn") else p.get("url")) or ""
    feats = "".join(f"<li>{e(f)}</li>" for f in loc(p.get("features"), lang))
    if st == "live" and url:
        cta = f'<a class="btn sm" href="{e(url)}" target="_blank" rel="noopener">{e(t["product_cta_live"])} {e(p["name"])} →</a>'
    elif st == "soon":
        cta = f'<a class="btn sm ghost" href="{wa_link(p["name"] + " — " + t["product_cta_soon"])}" target="_blank" rel="noopener">{e(t["product_cta_soon"])}</a>'
    else:
        cta = f'<a class="btn sm" href="{wa_link(p["name"] + " — " + t["product_cta_demo"])}" target="_blank" rel="noopener">{e(t["product_cta_demo"])}</a>'
    return f"""<article class="prod" id="p-{e(p['id'])}" style="--pc:{e(p.get('color', '#0a6cff'))}">
<div class="prod-top"><span class="prod-ic" aria-hidden="true">{e(p.get('icon', '◆'))}</span><span class="badge {e(st)}">{e(t['status'].get(st, st))}</span></div>
<small>{e(loc(p.get('category'), lang))}</small>
<h3>{e(p['name'])}</h3>
<p class="tag">{e(loc(p.get('tagline'), lang))}</p>
<p>{e(loc(p.get('description'), lang))}</p>
<ul class="ticks">{feats}</ul>
<p class="meta">{e(p.get('platforms', ''))} · {e(p.get('languages', ''))}</p>
<div class="prod-cta">{cta}</div>
</article>"""

def products(t):
    order = {"live": 0, "ready": 1, "soon": 2}
    items = sorted(PRODUCTS, key=lambda p: order.get(p.get("status"), 3))
    cards = "".join(product_card(p, t) for p in items)
    return f"""<section class="sec" id="products"><div class="wrap">
<div class="head"><h2>{e(t['products_h'])}</h2><p>{e(t['products_p'])}</p></div>
<div class="prods">{cards}</div></div></section>"""

def services(t):
    tabs, panes = [], []
    for i, (name, intro, bullets, chips) in enumerate(t["services"], 1):
        sel = "true" if i == 1 else "false"
        tabs.append(f'<button class="tab" role="tab" id="t{i}" aria-selected="{sel}" aria-controls="s{i}">{e(name)}</button>')
        lis = "".join(f"<li>{e(b)}</li>" for b in bullets)
        ch = "".join(f"<span>{e(c)}</span>" for c in chips)
        hidden = "" if i == 1 else " hidden"
        panes.append(f'<div class="pane" id="s{i}" role="tabpanel" aria-labelledby="t{i}"{hidden}><h3>{e(name)}</h3><p>{e(intro)}</p><ul>{lis}</ul><div class="chips">{ch}</div></div>')
    return f"""<section class="sec alt" id="services"><div class="wrap">
<div class="head"><h2>{e(t['services_h'])}</h2><p>{e(t['services_p'])}</p></div>
<div class="svc"><div class="tabs" role="tablist" aria-label="Services">{''.join(tabs)}</div><div>{''.join(panes)}</div></div>
</div></section>
<section class="band"><div class="wrap"><h2>{t['band_h']}</h2><p>{e(t['band_p'])}</p></div></section>"""

def industries(t):
    cards = "".join(f'<div class="ind"><span aria-hidden="true">{i}</span><h3>{e(n)}</h3><p>{e(d)}</p></div>' for i, n, d in t["industries"])
    return f"""<section class="sec" id="industries"><div class="wrap">
<div class="head"><h2>{e(t['ind_h'])}</h2><p>{e(t['ind_p'])}</p></div>
<div class="inds">{cards}</div></div></section>"""

def packages(t):
    cards = []
    for name, sub, items in t["packages"]:
        lis = "".join(f"<li>{e(x)}</li>" for x in items)
        cards.append(f'<div class="pk"><h3>{e(name)}</h3><p>{e(sub)}</p><ul class="ticks">{lis}</ul><a class="btn sm ghost" href="{wa_link(name + " — " + t["pk_cta"])}" target="_blank" rel="noopener">{e(t["pk_cta"])}</a></div>')
    return f"""<section class="sec alt" id="packages"><div class="wrap">
<div class="head"><h2>{e(t['pk_h'])}</h2><p>{e(t['pk_p'])}</p></div>
<div class="pks">{''.join(cards)}</div></div></section>"""

def work(t):
    lang = t["lang"]
    cards = []
    for p in PROJECTS:
        cat = p.get("category_bn") if lang == "bn" and p.get("category_bn") else p.get("category", "")
        desc = p.get("description_bn") if lang == "bn" and p.get("description_bn") else p.get("description", "")
        img = f'<img src="/{e(p["image"])}" alt="{e(p["title"])}" loading="lazy" width="900" height="525">' if p.get("image") else ""
        link = f'<a class="vis" href="{e(p["url"])}" target="_blank" rel="noopener">Visit project →</a>' if p.get("url") else ""
        tech = "".join(f"<span>{e(x)}</span>" for x in p.get("technologies", []))
        cards.append(f'<article class="proj"><div class="proj-img">{img}</div><div class="proj-body"><small>{e(cat)}</small><h3>{e(p["title"])}</h3><p>{e(desc)}</p><div class="chips">{tech}</div>{link}</div></article>')
    return f"""<section class="sec" id="work"><div class="wrap">
<div class="head"><h2>{e(t['work_h'])}</h2><p>{e(t['work_p'])}</p></div>
<div class="grid3">{''.join(cards)}</div></div></section>"""

def why(t):
    items = "".join(f'<div class="why-i"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in t["why"])
    return f"""<section class="sec alt" id="why"><div class="wrap">
<div class="head"><h2>{e(t['why_h'])}</h2></div><div class="whys">{items}</div></div></section>"""

def process_caps(t):
    steps = "".join(f'<div class="step"><b>{i}</b><h3>{e(h)}</h3><p>{e(p)}</p></div>' for i, (h, p) in enumerate(t["process"], 1))
    caps = "".join(f'<div class="cap"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in t["caps"])
    return f"""<section class="sec" id="process"><div class="wrap">
<div class="head"><h2>{e(t['proc_h'])}</h2><p>{e(t['proc_p'])}</p></div>
<div class="steps">{steps}</div></div></section>
<section class="sec alt" id="capabilities"><div class="wrap">
<div class="head"><h2>{e(t['cap_h'])}</h2><p>{e(t['cap_p'])}</p></div>
<div class="caps">{caps}</div></div></section>"""

def faq(t):
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in t["faq"])
    return f"""<section class="sec" id="faq"><div class="wrap faq">
<h2>{e(t['faq_h'])}</h2><div class="qs">{items}</div></div></section>"""

def contact(t):
    f = t["form"]
    opts = "".join(f"<option>{e(o)}</option>" for o in f["types"])
    return f"""<section class="sec alt" id="contact"><div class="wrap contact">
<div><h2>{e(t['contact_h'])}</h2><p>{e(t['contact_p'])}</p>
<div class="cd"><a class="btn wa" href="{wa_link(t['wa_msg'])}" target="_blank" rel="noopener">WhatsApp {e(SITE['whatsapp_display'])}</a><a href="mailto:{SITE['email']}">{SITE['email']}</a><span>{e(SITE['region'])}</span></div></div>
<form action="https://formsubmit.co/{SITE['email']}" method="POST">
<input type="hidden" name="_subject" value="{e(f['subject'])}"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="_template" value="table"><input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<label>{e(f['name'])}<input name="name" required autocomplete="name"></label>
<label>{e(f['email'])}<input name="email" type="email" required autocomplete="email" placeholder="you@company.com"></label>
<label>{e(f['phone'])}<input name="phone" type="tel" autocomplete="tel" inputmode="tel"></label>
<label>{e(f['type'])}<select name="service">{opts}</select></label>
<label>{e(f['msg'])}<textarea name="message" rows="5" required></textarea></label>
<button class="btn" type="submit">{e(f['send'])}</button>
</form></div></section>"""

def footer(t, home):
    svc = "".join(f'<li><a href="{home}#services">{e(s[0])}</a></li>' for s in t["services"])
    prods = "".join(
        f'<li><a href="{e(p["url"]) if p.get("status") == "live" and p.get("url") else home + "#p-" + e(p["id"])}">{e(p["name"])}</a></li>'
        for p in PRODUCTS)
    comp = "".join(f'<li><a href="{home}{h}">{e(l)}</a></li>' for h, l in t["foot_company_links"])
    return f"""<footer class="foot"><div class="wrap">
<div class="foot-top">
<div><img src="/assets/img/logo-dark.webp" alt="Sarvenex" width="176" height="30" loading="lazy"><p>{e(t['foot_about'])}</p><p class="small">{e(t['udyam'])} · {e(SITE['region'])}</p></div>
<div><h4>{e(t['foot_products'])}</h4><ul>{prods}</ul></div>
<div><h4>{e(t['foot_services'])}</h4><ul>{svc}</ul></div>
<div><h4>{e(t['foot_talk'])}</h4><ul><li><a href="{wa_link(t['wa_msg'])}" target="_blank" rel="noopener">WhatsApp</a></li><li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>{comp}<li><a href="/privacy.html">{e(t['privacy'])}</a></li><li><a href="{t['other_href']}" lang="{t['other_lang']}">{e(t['other_label'])}</a></li></ul></div>
</div>
<p class="foot-word" aria-hidden="true">SARVENEX</p>
<div class="foot-bot"><span>© <span id="year">{datetime.date.today().year}</span> Sarvenex. {e(t['rights'])}</span><nav><a href="/privacy.html">{e(t['privacy'])}</a><a href="#top">{e(t['top'])}</a></nav></div>
</div></footer>
<a class="wa-float" href="{wa_link(t['wa_msg'])}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true"><path fill="currentColor" d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7a10.7 10.7 0 0 1-5.5-1.5l-.4-.2-3.9 1 1-3.8-.2-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-1-2.2-1s-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1a8.8 8.8 0 0 1-4.3-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.9.4 3.7 3.7 0 0 0-1.1 2.7 6.4 6.4 0 0 0 1.3 3.4 14.7 14.7 0 0 0 5.7 5c2.1.9 2.9 1 4 .8a3.4 3.4 0 0 0 2.2-1.6 2.8 2.8 0 0 0 .2-1.6c-.1-.2-.3-.3-.6-.4z"/></svg></a>
<script src="/assets/js/main.js" defer></script>
</body></html>
"""

# ---------------------------------------------------------------- schema
def schema(t):
    lang = t["lang"]
    org = {
        "@type": ["Organization", "ProfessionalService"],
        "@id": D + "/#org",
        "name": "Sarvenex",
        "url": D + "/",
        "logo": D + "/assets/img/sarvenex-icon.png",
        "image": D + "/assets/img/og-image.png",
        "slogan": SITE["tagline"],
        "description": T["en"]["description"],
        "email": SITE["email"],
        "telephone": "+" + SITE["whatsapp"],
        "address": {"@type": "PostalAddress", "addressLocality": "Nadia", "addressRegion": "West Bengal", "addressCountry": "IN"},
        "areaServed": {"@type": "Country", "name": "India"},
        "knowsLanguage": ["en", "bn", "hi"],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s[0]}} for s in T["en"]["services"]],
    }
    if SITE["social"]:
        org["sameAs"] = list(SITE["social"].values())
    apps = []
    for p in PRODUCTS:
        a = {"@type": "SoftwareApplication", "name": p["name"],
             "description": loc(p.get("description"), "en"),
             "applicationCategory": p.get("schema", {}).get("applicationCategory", "BusinessApplication"),
             "operatingSystem": p.get("schema", {}).get("operatingSystem", "Android, Web"),
             "publisher": {"@id": D + "/#org"}}
        if p.get("url"):
            a["url"] = p["url"]
        apps.append(a)
    faq_ld = {"@type": "FAQPage", "inLanguage": lang,
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}
    site = {"@type": "WebSite", "@id": D + "/#website", "url": D + "/", "name": "Sarvenex", "inLanguage": ["en", "bn"], "publisher": {"@id": D + "/#org"}}
    items = {"@type": "ItemList", "name": "Sarvenex products", "itemListElement": [{"@type": "ListItem", "position": i, "item": a} for i, a in enumerate(apps, 1)]}
    return {"@context": "https://schema.org", "@graph": [org, site, items, faq_ld]}

# ---------------------------------------------------------------- pages
def home_page(lang):
    t = T[lang]
    body = "".join([hero(t), products(t), services(t), industries(t), packages(t), work(t), why(t), process_caps(t), faq(t), contact(t)])
    return head(t, t["dir"], schema(t)) + "\n" + header(t, "") + f'\n<main id="main">{body}</main>\n' + footer(t, "")

def privacy_page():
    t = dict(T["en"])
    t.update(title="Privacy policy — Sarvenex", description="How Sarvenex collects, uses and protects your personal information.")
    with open(os.path.join(ROOT, "tools", "privacy_body.html"), encoding="utf-8") as f:
        body = f.read()
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Privacy policy", "url": D + "/privacy.html", "publisher": {"@type": "Organization", "name": "Sarvenex", "url": D + "/"}}
    h = head(t, "/privacy.html", ld).replace('<link rel="alternate" hreflang="bn" href="https://sarvenex.com/bn/">\n', "")
    return h + "\n" + header(t, "/") + f'\n<main id="main">{body}</main>\n' + footer(t, "/")

def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", rel)

def main():
    write("index.html", home_page("en"))
    write("bn/index.html", home_page("bn"))
    write("privacy.html", privacy_page())
    urls = [("/", "1.0"), ("/bn/", "0.9"), ("/privacy.html", "0.3")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u, pr in urls:
        alt = ""
        if u in ("/", "/bn/"):
            alt = f'<xhtml:link rel="alternate" hreflang="en" href="{D}/"/><xhtml:link rel="alternate" hreflang="bn" href="{D}/bn/"/>'
        sm.append(f"<url><loc>{D}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority>{alt}</url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {D}/sitemap.xml\n")

if __name__ == "__main__":
    main()
