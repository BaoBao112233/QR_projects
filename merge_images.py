import json
from pathlib import Path

base = Path("d:/Projects/QR_projects")
products = json.loads((base / "lubylab_products.json").read_text(encoding="utf-8"))
imgs = json.loads((base / "lubylab_images_full.json").read_text(encoding="utf-8"))


def dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def filter_thumbs(urls):
    """Keep only product thumbnails dated >= 2025 (skip brand logos / decorative)."""
    out = []
    for u in urls:
        # remove duplicates with ?w= variants
        if "/thumbnail/" not in u:
            continue
        # exclude tiny logos already filtered
        out.append(u)
    return out


def filter_details(urls):
    """Detail banners — keep imweb upload-bucket items only."""
    out = []
    for u in urls:
        # Strip ?w= query for canonical detail original
        if "/upload/" in u or "cdn-optimized.imweb.me/upload" in u:
            out.append(u)
    return out


for prod in products["products"]:
    key = prod["key"]
    info = imgs.get(key, {})
    all_urls = info.get("all", [])

    # Detail banners — strip ?w= duplicates by keeping highest-resolution form
    details_raw = [u for u in all_urls if "/upload/" in u]
    # Group by base path, prefer the one with largest ?w= or no ?w
    by_base = {}
    for u in details_raw:
        base_url = u.split("?")[0]
        existing = by_base.get(base_url)
        if existing is None:
            by_base[base_url] = u
        else:
            # Pick the one with higher ?w=
            def w(x):
                if "?w=" in x:
                    try:
                        return int(x.split("?w=")[1].split("&")[0])
                    except Exception:
                        return 0
                return 99999  # original (no resize) ranked highest
            if w(u) > w(existing):
                by_base[base_url] = u
    details = list(by_base.values())

    # Keep current thumbnail structure but supplement from new crawl
    cur_main = prod["images"]["main"] if isinstance(prod["images"], dict) else None
    cur_gallery = prod["images"]["gallery"] if isinstance(prod["images"], dict) else []
    extra_thumbs = [u for u in all_urls if "/thumbnail/" in u and u not in cur_gallery and u != cur_main]
    gallery_full = dedupe(cur_gallery + extra_thumbs)

    prod["images"] = {
        "main": cur_main,
        "gallery": gallery_full,
        "detail_banners": details,
    }

(base / "lubylab_products.json").write_text(
    json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8"
)

# Print summary
for p in products["products"]:
    img = p["images"]
    print(f"{p['key']}: gallery={len(img['gallery'])}  detail_banners={len(img['detail_banners'])}")
