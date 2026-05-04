import json
from pathlib import Path

p = Path("d:/Projects/QR_projects/lubylab_products.json")
data = json.loads(p.read_text(encoding="utf-8"))

BLOCK = ["1a7a3fc45bf15", "81cc7e1db6a23", "default_profile",
         "kakao", "npay_logo", "vendor-cdn.imweb.me",
         "/thumbnail/20240226/"]

def keep(u):
    return u and not any(b in u for b in BLOCK)

removed = 0
for prod in data["products"]:
    img = prod["images"]
    before = len(img.get("gallery", []))
    img["gallery"] = [u for u in img.get("gallery", []) if keep(u)]
    img["detail_banners"] = [u for u in img.get("detail_banners", []) if keep(u)]
    after = len(img["gallery"])
    if before != after:
        print(f"{prod['key']}: gallery {before} -> {after}")
        removed += before - after

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Total removed gallery items: {removed}")
