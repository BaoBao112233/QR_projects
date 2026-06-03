"""
Optimize site/data images for production:
  - Convert PNG/JPG -> WebP (much smaller for these banner/photo images)
  - Downscale anything wider than MAX_WIDTH (web display never needs more)
  - Delete the original PNG/JPG from the served folder (originals stay in git history)
  - Rewrite ../data/*.png|jpg references in lubylab_products.json -> .webp

Run once, then re-run generate_site.py to rebuild the product pages.
"""
import re
import sys
from pathlib import Path

from PIL import Image

BASE = Path("d:/Projects/QR_projects")
DATA = BASE / "site" / "data"
JSON = BASE / "lubylab_products.json"

MAX_WIDTH = 1080      # plenty for full-width mobile/desktop banners
QUALITY = 82          # visually lossless for this kind of content
SRC_EXTS = {".png", ".jpg", ".jpeg"}


def convert(path: Path) -> tuple[int, int]:
    """Convert one image to .webp next to it, downscaling if needed.

    Returns (bytes_before, bytes_after).
    """
    before = path.stat().st_size
    with Image.open(path) as im:
        im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
        if im.width > MAX_WIDTH:
            ratio = MAX_WIDTH / im.width
            im = im.resize((MAX_WIDTH, round(im.height * ratio)), Image.LANCZOS)
        out = path.with_suffix(".webp")
        im.save(out, "WEBP", quality=QUALITY, method=6)
    after = out.stat().st_size
    return before, after


def main() -> None:
    files = [p for p in DATA.rglob("*") if p.suffix.lower() in SRC_EXTS]
    if not files:
        print("No PNG/JPG found under", DATA)
        return

    total_before = total_after = 0
    for i, p in enumerate(files, 1):
        try:
            b, a = convert(p)
            total_before += b
            total_after += a
            p.unlink()  # remove original from served folder (kept in git history)
            if i % 50 == 0 or i == len(files):
                print(f"  [{i}/{len(files)}] {total_before/1e6:.0f}MB -> {total_after/1e6:.0f}MB")
        except Exception as e:  # noqa: BLE001
            print(f"  SKIP {p}: {e}", file=sys.stderr)

    print(f"\nImages: {len(files)} converted")
    print(f"Disk: {total_before/1e6:.1f}MB -> {total_after/1e6:.1f}MB "
          f"({100*(1-total_after/total_before):.0f}% smaller)")

    # Rewrite references in the products JSON: only ../data/ paths, only image exts.
    text = JSON.read_text(encoding="utf-8")
    new_text = re.sub(r'(\.\./data/[^"\\]+?)\.(?:png|jpg|jpeg)', r"\1.webp", text)
    n = text.count("../data/")
    JSON.write_text(new_text, encoding="utf-8")
    print(f"JSON: rewrote ~{n} ../data references -> .webp")
    print("\nNext: python generate_site.py  (rebuilds product pages with new refs)")


if __name__ == "__main__":
    main()
