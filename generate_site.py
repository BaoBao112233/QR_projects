import json
from pathlib import Path

base = Path("d:/Projects/QR_projects")
data = json.loads((base / "lubylab_products.json").read_text(encoding="utf-8"))
site_dir = base / "site"
products_dir = site_dir / "products"
products_dir.mkdir(parents=True, exist_ok=True)


def slug(key: str) -> str:
    return key.lower().replace(" ", "-").replace("+", "plus")


# Maps each product "key" to its product id on the global storefront. Clicking a
# card or opening a sub-page redirects to https://www.lubylabglobal.com/#/product?id=<id>.
GLOBAL_BASE = "https://www.lubylabglobal.com/#/product?id="
GLOBAL_IDS = {
    "NAD": 14,
    "Cica Ampoule": 8,
    "Cica Cream": 9,
    "NAD Sculp Matrix": 15,
    "Pore Peeling Pad": 7,
    "Hyper Spishot": 2,
    "Vitamin C Ball": 27,
    "Glutathione Ppuder": 4,
    "Retinal Shot": 20,
    "Peachy Tone-Up UV Fluid": 3,
    "MAV Cream": 18,
    "TAM Ampoule": 30,
    "Waterful Tone-Up Blue Shield": 11,
}

# Legacy sub-page slugs kept alive so existing QR codes still resolve. Each maps
# to the global product id of its current equivalent.
LEGACY_REDIRECTS = {
    "peachy-tone-up": 3,
    "waterful-tone-up": 11,
}


def global_url(product) -> str:
    pid = GLOBAL_IDS[product["key"]]
    return f"{GLOBAL_BASE}{pid}"


def redirect_page(url: str, name: str = "") -> str:
    # Self-contained: no relative asset refs, so it works wherever it is deployed
    # (e.g. served at https://www.lubylabglobal.com/site/products/<slug>.html).
    url_json = json.dumps(url)
    label = name or "the product page"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LUBYLAB</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({url_json});</script>
</head>
<body>
<p>Redirecting to <a href="{url}">{label}</a>…</p>
</body>
</html>
"""


def page(product) -> str:
    url = global_url(product)
    name = product.get("name", {}).get("en", "")
    return redirect_page(url, name)


def index_page(products) -> str:
    cards = []
    for p in products:
        s = slug(p["key"])
        cards.append({
            "slug": s,
            "key": p["key"],
            "name": p["name"],
            "price": p["price"],
            "img": p["images"]["main"],
            "url": global_url(p),
        })
    cards_json = json.dumps(cards, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LUBYLAB — Products</title>
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/favicon.png">
<link rel="stylesheet" href="assets/styles.css">
<script src="assets/i18n.js" defer></script>
<script>window.PRODUCTS = {cards_json};</script>
<script>
const FX = {{ USD: 1/1360, CNY: 1/188 }};
function parseKRW(s) {{ const m = String(s||'').replace(/[^\\d]/g,''); return m? parseInt(m,10): null; }}
function formatRange(v, code) {{
  const low = Math.floor(v*0.985), high = Math.ceil(v*1.015);
  return `${{low.toLocaleString('en-US')}}–${{high.toLocaleString('en-US')}} ${{code}}`;
}}
function priceLabel(price) {{
  const loc = LUBY.getLocale() || LUBY.DEFAULT_LOCALE;
  const krw = parseKRW(price);
  if (!krw) return price;
  if (loc === 'en') return `${{price}} <span class="card-approx">≈ ${{formatRange(krw*FX.USD,'USD')}}</span>`;
  if (loc === 'zh') return `${{price}} <span class="card-approx">≈ ${{formatRange(krw*FX.CNY,'CNY')}}</span>`;
  return price;
}}
document.addEventListener('DOMContentLoaded', async () => {{
  await LUBY.ensureLocale();
  document.title = LUBY.t('indexTitle') + ' — LUBYLAB';
  const tb = document.querySelector('.topbar');
  tb.innerHTML = '<a href="index.html" class="brand"><img src="assets/logo.png" alt="LUBYLAB" class="brand-logo"></a><div class="lang-switch-wrap"></div>';
  LUBY.renderLangSwitch(tb.querySelector('.lang-switch-wrap'), () => location.reload());
  document.getElementById('idx-title').textContent = LUBY.t('indexTitle');
  document.getElementById('idx-sub').textContent = LUBY.t('indexSub');
  const grid = document.getElementById('grid');
  grid.innerHTML = window.PRODUCTS.map(p => `
    <a class="product-card" href="${{p.url}}">
      <div class="img"><img src="${{p.img}}" alt="" loading="lazy"></div>
      <div class="body">
        <div class="key">${{p.key}}</div>
        <div class="name">${{LUBY.tr(p.name)}}</div>
      </div>
    </a>
  `).join('');
}});
</script>
</head>
<body>
<header class="topbar"></header>
<main class="index-page">
  <h1 id="idx-title">LUBYLAB Products</h1>
  <p class="sub" id="idx-sub">Discover our hero collection</p>
  <div class="product-grid" id="grid"></div>
</main>
</body>
</html>
"""


# Where the redirect sub-pages must live to be served on the global domain at
# https://www.lubylabglobal.com/site/products/<slug>.html. None = skip deploy.
DEPLOY_DIR = Path("d:/Projects/LANDING-PAGE/frontend/site/products")

redirect_pages = {}  # slug -> html, mirrored to the global site below

for prod in data["products"]:
    s = slug(prod["key"])
    html = page(prod)
    redirect_pages[s] = html
    (products_dir / f"{s}.html").write_text(html, encoding="utf-8")
    print(f"  -> products/{s}.html  ->  {global_url(prod)}")

for legacy_slug, pid in LEGACY_REDIRECTS.items():
    url = f"{GLOBAL_BASE}{pid}"
    html = redirect_page(url)
    redirect_pages[legacy_slug] = html
    (products_dir / f"{legacy_slug}.html").write_text(html, encoding="utf-8")
    print(f"  -> products/{legacy_slug}.html  ->  {url}")

(site_dir / "index.html").write_text(index_page(data["products"]), encoding="utf-8")
print("  -> index.html")

if DEPLOY_DIR.parent.parent.exists():
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    for s, html in redirect_pages.items():
        (DEPLOY_DIR / f"{s}.html").write_text(html, encoding="utf-8")
    print(f"Deployed {len(redirect_pages)} redirect pages -> {DEPLOY_DIR}")
else:
    print(f"Skipped deploy (global site not found at {DEPLOY_DIR.parent.parent})")

print("Done.")
