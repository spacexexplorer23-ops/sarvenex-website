# Sarvenex website (sarvenex.com)

Static, bilingual (English + Bengali) company website with light/dark mode. Pages are
generated from data files by a small Python script, so the HTML is fully readable by
Google (no content loaded by JavaScript).

```
index.html        English home   (generated)
bn/index.html     Bengali home   (generated)
privacy.html      Privacy policy (generated)
sitemap.xml, robots.txt          (generated)
tools/content.py                 All page text, EN + BN, and site settings (WhatsApp, email)
tools/privacy_body.html          Privacy policy body
tools/build.py                   Generator (Python 3, standard library only)
assets/data/products.json        Sarvenex's own products
assets/data/projects.json        Portfolio / client work
```

## Build

```
python tools/build.py
```

Run it after any change in `tools/` or `assets/data/`, then commit the generated files.
Azure Static Web Apps deploys the repo root on every push to `main`.

## Add a new product

Add an object to `assets/data/products.json`:

```json
{
  "id": "my-product",
  "name": "My Product",
  "status": "soon",               // live | ready | soon
  "url": "https://my-product.sarvenex.com/",
  "url_bn": "https://my-product.sarvenex.com/bn/",   // optional
  "icon": "⭐",
  "color": "#0A6CFF",
  "category": { "en": "Who it is for", "bn": "কাদের জন্য" },
  "tagline": { "en": "One line", "bn": "এক লাইনে" },
  "description": { "en": "Two sentences.", "bn": "দুই বাক্যে।" },
  "features": { "en": ["A", "B", "C", "D"], "bn": ["ক", "খ", "গ", "ঘ"] },
  "platforms": "Android · Web",
  "languages": "বাংলা · English",
  "schema": { "applicationCategory": "BusinessApplication", "operatingSystem": "Android, Web" }
}
```

Then run the build. The product appears on both languages, in the footer, and in the
structured data (schema.org ItemList of SoftwareApplication) automatically.

- `live` + `url` → "Visit" button
- `ready` → "Ask for a demo" (opens WhatsApp)
- `soon` → "Get notified" (opens WhatsApp)

## Add portfolio work

Add to `assets/data/projects.json` (`title`, `category`, `description`, optional
`category_bn`, `description_bn`, `technologies`, `image`, `url`). Use a ~900×525 WebP
image in `assets/img/projects/`.

## Change contact details

Edit `SITE` at the top of `tools/content.py` (WhatsApp number, email, social profile
URLs for schema `sameAs`), then build.

## Preview locally

```
python -m http.server 8000
```

Open http://localhost:8000 and http://localhost:8000/bn/.
