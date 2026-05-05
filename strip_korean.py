import json
import re
from pathlib import Path

base = Path("d:/Projects/QR_projects")


def strip_kr(obj):
    if isinstance(obj, dict):
        obj.pop("kr", None)
        for v in obj.values():
            strip_kr(v)
    elif isinstance(obj, list):
        for v in obj:
            strip_kr(v)
    return obj


def clean_value(s: str) -> str:
    if not isinstance(s, str):
        return s
    # Replace Korean currency / point markers
    s = s.replace("원", " KRW")
    s = re.sub(r"\s*포인트", " points", s)
    return re.sub(r"\s+", " ", s).strip()


def clean_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                obj[k] = clean_value(v)
            else:
                clean_strings(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                obj[i] = clean_value(v)
            else:
                clean_strings(v)


def process(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    strip_kr(data)
    clean_strings(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Cleaned {path}")


process(base / "lubylab_products.json")
process(base / "lubylab_images_full.json")
print("Done.")
