import json
from pathlib import Path

base = Path("d:/Projects/QR_projects")
data = json.loads((base / "lubylab_products.json").read_text(encoding="utf-8"))
site_dir = base / "site"
products_dir = site_dir / "products"
products_dir.mkdir(parents=True, exist_ok=True)


def slug(key: str) -> str:
    return key.lower().replace(" ", "-").replace("+", "plus")


def page(product) -> str:
    json_blob = json.dumps(product, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LUBYLAB</title>
<link rel="icon" type="image/png" href="../assets/favicon.png">
<link rel="apple-touch-icon" href="../assets/favicon.png">
<link rel="stylesheet" href="../assets/styles.css">
<script src="../assets/i18n.js" defer></script>
<script>window.PRODUCT = {json_blob};</script>
<script src="../assets/product.js" defer></script>
</head>
<body>
<header class="topbar"></header>
<main class="product-page"><div class="product-main"></div></main>
</body>
</html>
"""


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
    <a class="product-card" href="products/${{p.slug}}.html">
      <div class="img"><img src="${{p.img}}" alt="" loading="lazy"></div>
      <div class="body">
        <div class="key">${{p.key}}</div>
        <div class="name">${{LUBY.tr(p.name)}}</div>
        <div class="price">${{priceLabel(p.price)}}</div>
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


for prod in data["products"]:
    s = slug(prod["key"])
    (products_dir / f"{s}.html").write_text(page(prod), encoding="utf-8")
    print(f"  -> products/{s}.html")

(site_dir / "index.html").write_text(index_page(data["products"]), encoding="utf-8")
print("  -> index.html")
print("Done.")
