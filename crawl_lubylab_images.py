import json
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PRODUCTS = [
    {"key": "NAD",                "url": "https://www.lubylab.co.kr/shop_view/?idx=45"},
    {"key": "Cica",               "url": "https://www.lubylab.co.kr/shop_view/?idx=38"},
    {"key": "NAD Sculp Matrix",   "url": "https://www.lubylab.co.kr/shop_view/?idx=46"},
    {"key": "Pore Peeling Pad",   "url": "https://www.lubylab.co.kr/shop_view/?idx=31"},
    {"key": "Hyper Spishot",      "url": "https://www.lubylab.co.kr/beauty/?idx=33"},
    {"key": "Vitamin C Ball",     "url": "https://www.lubylab.co.kr/beauty/?idx=48"},
    {"key": "Glutathione Ppuder", "url": "https://www.lubylab.co.kr/beauty/?idx=39"},
    {"key": "Retinal Shot",       "url": "https://www.lubylab.co.kr/shop_view/?idx=54"},
]

EXCLUDE_PATTERNS = [
    "vendor-cdn.imweb.me",
    "default_profile",
    "kakao",
    "npay_logo",
    "1a7a3fc45bf15",
    "81cc7e1db6a23",
]

URL_RE = re.compile(r"https?://[^\s\"'<>()]+\.(?:jpg|jpeg|png|webp|gif)(?:\?[^\s\"'<>]*)?", re.I)


def is_relevant(u: str) -> bool:
    if any(p in u for p in EXCLUDE_PATTERNS):
        return False
    if "imweb.me" not in u:
        return False
    return True


def crawl(page, url: str):
    page.goto(url, wait_until="networkidle", timeout=60000)
    # Click on detail/description tab to force-load detail images
    for sel in [
        "text=상세정보", "text=상세 정보", "text=DETAIL", "text=Detail",
        "text=상품정보", "text=상품 정보",
    ]:
        try:
            page.locator(sel).first.click(timeout=1500)
            page.wait_for_timeout(800)
            break
        except Exception:
            pass

    # Scroll to bottom slowly to trigger lazy-load images
    last_h = 0
    for _ in range(40):
        page.evaluate("window.scrollBy(0, 1200)")
        page.wait_for_timeout(350)
        h = page.evaluate("document.body.scrollHeight")
        if h == last_h:
            break
        last_h = h

    page.wait_for_timeout(1500)

    # Extract all <img> sources + data-src + style backgrounds + raw HTML matches
    sources = page.evaluate(
        """
        () => {
            const out = new Set();
            document.querySelectorAll('img').forEach(img => {
                ['src','data-src','data-original','data-lazy','data-srcset'].forEach(a => {
                    const v = img.getAttribute(a);
                    if (v) v.split(',').forEach(s => out.add(s.trim().split(' ')[0]));
                });
                if (img.currentSrc) out.add(img.currentSrc);
            });
            document.querySelectorAll('[style*="background"]').forEach(el => {
                const m = el.getAttribute('style').match(/url\\(([^)]+)\\)/g);
                if (m) m.forEach(x => out.add(x.replace(/url\\(|\\)|['"]/g, '')));
            });
            return Array.from(out);
        }
        """
    )
    html = page.content()
    sources += URL_RE.findall(html)

    # Normalize and dedupe in stable order
    seen, ordered = set(), []
    for s in sources:
        if not s:
            continue
        s = s.strip()
        if s.startswith("//"):
            s = "https:" + s
        if not s.startswith("http"):
            continue
        if not is_relevant(s):
            continue
        if s in seen:
            continue
        seen.add(s)
        ordered.append(s)
    return ordered


def categorize(urls):
    """Split into thumbnail/main and detail/upload sections."""
    thumbs, details = [], []
    for u in urls:
        if "/upload/" in u or "S2024" in u or "S2025" in u or "S2026" in u:
            details.append(u)
        else:
            thumbs.append(u)
    return thumbs, details


def main():
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        )
        page = ctx.new_page()
        for p in PRODUCTS:
            print(f"[{p['key']}] {p['url']}")
            urls = crawl(page, p["url"])
            thumbs, details = categorize(urls)
            print(f"  thumbnails={len(thumbs)}  details={len(details)}")
            out[p["key"]] = {
                "url": p["url"],
                "thumbnails": thumbs,
                "details": details,
                "all": urls,
            }
        browser.close()

    Path("d:/Projects/QR_projects/lubylab_images_full.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Saved -> lubylab_images_full.json")


if __name__ == "__main__":
    main()
