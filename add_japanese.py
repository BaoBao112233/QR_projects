import json
from pathlib import Path

p = Path("d:/Projects/QR_projects/lubylab_products.json")
data = json.loads(p.read_text(encoding="utf-8"))

# Japanese translations keyed by product key
JA = {
    "NAD": {
        "name": "NAD+ GFブースタークリーム",
        "status": "売り切れ",
        "exclusive": "レディヤング薬局限定販売商品",
        "description": "NAD+と成長因子(Growth Factor)を配合したブースタークリーム",
        "shipping": "宅配 · 送料無料",
        "delivery_note": "当日発送商品 (本日12:00までのお支払い)",
        "main_ingredients": ["NAD+", "成長因子 (Growth Factor)"],
    },
    "Cica Ampoule": {
        "name": "デュアルPGAハイドロシカアンプル",
        "status": "ベスト · ホット",
        "category": "エッセンス / アンプル",
        "main_feature": "シカコンプレックスが外部刺激で敏感になった肌を鎮静ケア",
        "shipping": "宅配 · 送料無料",
        "delivery_note": "本日12:00までのお支払いで当日発送可能",
        "key_benefits": [
            "速やかな鎮静ケア",
            "うるおい補給",
            "美白 & シワ改善"
        ],
        "main_ingredients": [
            "デュアルPGA (ポリグルタミン酸)",
            "シカコンプレックス"
        ],
    },
    "NAD Sculp Matrix": {
        "name": "スカルプマトリックスアンプル",
        "category": "アンプル / エッセンス",
        "main_feature": "肌の土台を強化し、密度と弾力を満たすアンプル",
        "shipping": "宅配 · 送料無料",
        "delivery_note": "当日発送 (平日12:00までのお支払い)",
        "key_benefits": [
            "ボリュームリフティング",
            "弾力強化",
            "肌のキメ整え"
        ],
    },
    "Pore Peeling Pad": {
        "name": "ポアピーリングパッド",
        "category": "パッド型スキンケア",
        "description": "角質•凹凸を整え、鎮静と水分を残すデイリールーティンパッド",
        "shipping": "宅配 · 送料無料",
        "delivery_note": "当日発送商品 (平日12:00まで)",
        "key_benefits": [
            "角質除去",
            "複合鎮静",
            "保湿膜ケア",
            "うるおいケア"
        ],
    },
    "Hyper Spishot": {
        "name": "ハイパー ルビースピショット",
        "key_feature": "第4世代ハイブリッドスピキュール技術 — 刺激を抑えながら明るく華やかなツヤを演出",
        "shipping": "宅配 · 送料無料",
        "delivery_note": "当日発送商品 (平日12:00までのお支払い)",
        "key_benefits": [
            "うるおいケア",
            "保湿膜強化",
            "シワ改善",
            "肌のキメ整え"
        ],
    },
    "Vitamin C Ball": {
        "name": "クリスタル エッセンス パウダーボール",
        "main_feature": "純粋ビタミンCとナイアシンアミドを配合したパウダーボールタイプの美白・ブライトニング製品",
        "shipping": "宅配 · 送料無料",
        "key_benefits": [
            "美白 / ブライトニング",
            "ツヤ・輝きアップ",
            "シミ・くすみケア"
        ],
        "main_ingredients": [
            "純粋ビタミンC",
            "ナイアシンアミド"
        ],
    },
    "Glutathione Ppuder": {
        "name": "グルタチオン コラーゲン パウダーアンプル",
        "main_feature": "粉末状の濃縮アンプル",
        "shipping": "送料無料",
        "key_benefits": [
            "くすんだ肌色を明るく整える",
            "肌の弾力強化"
        ],
        "main_ingredients": [
            "グルタチオン",
            "低分子コラーゲン",
            "ナイアシンアミド",
            "7種の保湿レイヤー"
        ],
    },
    "Retinal Shot": {
        "name": "レチナール デュアル アクティブ スポット クリーム",
        "category": "スポットクリーム",
        "shipping": "宅配 · 送料無料",
        "main_ingredients": ["レチナール (Retinaldehyde)"],
        "key_benefits": [
            "シワ改善",
            "ピンポイント集中ケア"
        ],
    },
}


def add_ja(field, ja_value):
    """If field is a {kr,en,zh} dict, add ja key."""
    if isinstance(field, dict) and ("kr" in field or "en" in field or "zh" in field):
        field["ja"] = ja_value
        return field
    return field


for prod in data["products"]:
    ja = JA.get(prod["key"], {})
    for fname, ja_val in ja.items():
        if fname not in prod:
            continue
        cur = prod[fname]
        if isinstance(cur, list):
            # list of {kr,en,zh} dicts — pair by index
            if isinstance(ja_val, list) and len(ja_val) == len(cur):
                for i, item in enumerate(cur):
                    add_ja(item, ja_val[i])
        elif isinstance(cur, dict):
            add_ja(cur, ja_val)


# Brand also gets ja
data["brand"]["ja"] = "LUBYLAB (ルビーラボ)"

# Notes — add Japanese versions
ja_notes = [
    "詳細情報 (容量・全成分・使用方法) は詳細ページに画像として掲載されているため、HTMLからは抽出できませんでした。",
    "「Vitamin C Ball」はサイト内で純粋ビタミンCを配合した唯一のパウダーボール製品「Crystal Essence Powder Ball (idx=48)」に対応しています。",
    "NAD製品 (idx=45) は現在売り切れで、レディヤング薬局限定販売商品です。",
]
for i, note in enumerate(data.get("notes", [])):
    if i < len(ja_notes):
        note["ja"] = ja_notes[i]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Japanese translations added.")
