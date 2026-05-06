"""
Append newly added images in site/data/<product>/<LANG>/ to detail_banners
in lubylab_products.json. Existing banners are preserved; new images are
appended in natural sort order.
"""
import json
import re
from pathlib import Path

ROOT = Path("d:/Projects/QR_projects")
JSON_PATH = ROOT / "lubylab_products.json"
DATA_ROOT = ROOT / "site" / "data"
SITE_PRODUCTS = ROOT / "site" / "products"  # detail_banners use ../data/... relative to site/products/
EXTS = {".png", ".jpg", ".jpeg", ".webp"}

LANG_TO_FOLDER = {"en": "EN", "zh": "CN", "ja": "JP"}

def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = []
    for prod in data["products"]:
        db = prod.get("images", {}).get("detail_banners", {})
        if not db:
            continue

        # Detect product folder name from any existing banner path.
        sample = None
        for lang_arr in db.values():
            if lang_arr:
                sample = lang_arr[0]
                break
        if not sample:
            continue
        # ../data/<ProductFolder>/<LANG>/<file>
        m = re.match(r"\.\./data/([^/]+)/", sample)
        if not m:
            continue
        product_folder = m.group(1)

        for lang, lang_folder in LANG_TO_FOLDER.items():
            existing = db.get(lang, [])
            existing_names = {Path(p).name for p in existing}

            disk_dir = DATA_ROOT / product_folder / lang_folder
            if not disk_dir.exists():
                continue

            disk_files = [
                p.name for p in disk_dir.iterdir()
                if p.is_file() and p.suffix.lower() in EXTS
            ]
            # New = on disk but not in JSON
            new_files = sorted(
                [n for n in disk_files if n not in existing_names],
                key=natural_key,
            )
            if not new_files:
                continue

            new_paths = [f"../data/{product_folder}/{lang_folder}/{n}" for n in new_files]
            db[lang] = existing + new_paths
            summary.append((prod["key"], lang, len(new_paths), new_files))

        prod.setdefault("images", {})["detail_banners"] = db

    # Write back preserving Unicode (no \uXXXX escapes) and 2-space indent.
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if not summary:
        print("No new images found. detail_banners unchanged.")
        return

    print("Appended new banners:")
    by_product = {}
    for key, lang, count, names in summary:
        by_product.setdefault(key, []).append((lang, count, names))

    total = 0
    for key, rows in by_product.items():
        print(f"\n  {key}:")
        for lang, count, names in rows:
            total += count
            preview = ", ".join(names[:5]) + (f" ... (+{len(names)-5} more)" if len(names) > 5 else "")
            print(f"    {lang}: +{count}  [{preview}]")
    print(f"\nTotal images added: {total}")

if __name__ == "__main__":
    main()
