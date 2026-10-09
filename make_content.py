#!/usr/bin/env python3
"""Assemble content.json from .scrape/i18n.json (one-off migration script).

內容母本是 content.json；本腳本僅在需要重新從抓取備份生成時使用。
專家照片、頁面配圖已本地化的情況下，直接改 content.json 即可。
"""
import json

i18n = json.load(open('.scrape/i18n.json', encoding='utf-8'))

# 專家照片：原站 Hostinger CDN URL -> 本地 webp
EXPERT_IMAGES = {
    'Massimo Giovanni Lemma': 'expert-lemma.webp',
    'Francesco Lavarra': 'expert-lavarra.webp',
    'Marcio Scorsin': 'expert-scorsin.webp',
    'Andrea Mangini': 'expert-mangini.webp',
    'Vasile Sirbu': 'expert-sirbu.webp',
    'Kristian Desa': 'expert-desa.webp',
}
for lang in i18n:
    for exp in i18n[lang]['advisoryBoardNew']['experts']:
        exp['image'] = EXPERT_IMAGES[exp['enName']]

languages = [
    {"code": "en", "label": "English", "flag": "🇬🇧"},
    {"code": "zh-TW", "label": "繁體中文", "flag": "🇲🇴"},
    {"code": "zh-CN", "label": "简体中文", "flag": "🇨🇳"},
    {"code": "pt", "label": "Português", "flag": "🇵🇹"},
]

# 首頁統計數字（原站硬編碼在 JS 中，不在 i18n 內）
stats = [
    {"number": "47+", "key": "experts", "icon": "users"},
    {"number": "23", "key": "network", "icon": "globe"},
    {"number": "12+", "key": "cardiology", "icon": "heart"},
    {"number": "89%", "key": "supply", "icon": "box"},
]

# 頁面配圖（assets/img/ 下的本地文件）
images = {
    "hero_home": "hero-home.webp",
    "about_mission": "about-mission.webp",
    "about_presence": "about-presence.webp",
    "advisory_hero": "advisory-hero.webp",
    "service_trade": "service-trade.webp",
    "service_consulting": "service-consulting.webp",
    "service_premium": "about-mission.webp",
}

content = {
    "languages": languages,
    "default_lang": "en",
    "site_name": "澳門橋霍頓有限公司",
    "site_name_en": "United Macao Bridge Holden Corporation Limited",
    "site_url": "https://bridgeholdengroup.com",
    "email": "bridgeHolden@163.com",
    "whatsapp": "+853 66175570",
    "whatsapp_link": "https://wa.me/85366175570",
    "social": {"facebook": "#", "linkedin": "#", "twitter": "#"},
    "stats": stats,
    "images": images,
    "i18n": i18n,
}

with open('content.json', 'w', encoding='utf-8') as f:
    json.dump(content, f, ensure_ascii=False, indent=2)
print('content.json written:', len(json.dumps(content, ensure_ascii=False)), 'chars')
