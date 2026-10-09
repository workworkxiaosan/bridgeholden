#!/usr/bin/env python3
"""
澳門橋霍頓有限公司官網靜態站生成器
讀取 content.json，輸出多語言靜態 HTML 到 dist/。

用法:
    python3 build.py

更新網站內容 = 改 content.json → 重新執行 python3 build.py。
"""
import json, html, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
C = json.load(open(os.path.join(ROOT, 'content.json'), encoding='utf-8'))
I18N = C['i18n']
LANGS = [l['code'] for l in C['languages']]
DEFAULT = C['default_lang']
PAGES = ['index', 'about', 'services', 'advisory-board', 'success-stories', 'contact']
# 頁面 -> i18n nav 鍵
NAV_KEY = {'index': 'home', 'about': 'about', 'services': 'services',
           'advisory-board': 'advisoryBoard', 'success-stories': 'successStories', 'contact': 'contact'}

def esc(s): return html.escape(str(s), quote=True)

def t(lang, *keys):
    """取翻譯: t('en','nav','home')"""
    d = I18N[lang]
    for k in keys: d = d[k]
    return d

# ---------------- URL 規則 ----------------
# 默認語言 en 放根目錄（與原站默認語言一致），其他語言在 /zh-TW/ /zh-CN/ /pt/ 子目錄
def page_href(page, target_lang, current_lang):
    if target_lang == DEFAULT:
        target = 'index.html' if page == 'index' else f'{page}.html'
    else:
        target = f'{target_lang}/' + ('index.html' if page == 'index' else f'{page}.html')
    prefix = '../' if current_lang != DEFAULT else ''
    return prefix + target

def asset(path, current_lang):
    prefix = '../' if current_lang != DEFAULT else ''
    return prefix + 'assets/' + path

def abs_url(page, lang):
    base = C.get('site_url', 'https://bridgeholdengroup.com').rstrip('/')
    name = 'index.html' if page == 'index' else f'{page}.html'
    path = name if lang == DEFAULT else f'{lang}/{name}'
    return f'{base}/{path}'

# ---------------- 各語言固定文案（原站硬編碼為英文，遷移時本地化） ----------------
LBL = {
    'caseChallenge': {'zh-TW': '臨床挑戰', 'zh-CN': '临床挑战', 'en': 'Clinical Challenge', 'pt': 'Desafio Clínico'},
    'caseSolution': {'zh-TW': '解決方案', 'zh-CN': '解决方案', 'en': 'Solution', 'pt': 'Solução'},
    'caseOutcome': {'zh-TW': '治療結果', 'zh-CN': '治疗结果', 'en': 'Outcome', 'pt': 'Resultado'},
    'complianceNotice': {'zh-TW': '合規聲明', 'zh-CN': '合规声明', 'en': 'Compliance Notice', 'pt': 'Aviso de Conformidade'},
    'address': {'zh-TW': '地址', 'zh-CN': '地址', 'en': 'Address', 'pt': 'Endereço'},
    'email': {'zh-TW': '電子郵件', 'zh-CN': '电子邮件', 'en': 'Email', 'pt': 'E-mail'},
    'errRequired': {'zh-TW': '此欄位為必填', 'zh-CN': '此字段为必填', 'en': 'This field is required', 'pt': 'Este campo é obrigatório'},
    'errEmail': {'zh-TW': '電子郵件格式不正確', 'zh-CN': '电子邮件格式不正确', 'en': 'Invalid email format', 'pt': 'Formato de e-mail inválido'},
    'backHome': {'zh-TW': '返回首頁', 'zh-CN': '返回首页', 'en': 'Back to Home', 'pt': 'Voltar ao Início'},
    'notFound': {'zh-TW': '頁面不存在或已被移動', 'zh-CN': '页面不存在或已被移动',
                 'en': 'The page you are looking for does not exist or has been moved.',
                 'pt': 'A página que procura não existe ou foi movida.'},
}

def lbl(key, lang): return LBL[key][lang]

# ---------------- SVG 圖標（lucide 風格） ----------------
def icon(name, cls=''):
    P = {
        'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        'globe': '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        'heart': '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
        'box': '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
        'check-circle': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        'check': '<polyline points="20 6 9 17 4 12"/>',
        'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        'award': '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
        'map-pin': '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
        'mail': '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
        'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        'chevron-down': '<polyline points="6 9 12 15 18 9"/>',
        'menu': '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
        'close': '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        'facebook': '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
        'linkedin': '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
        'twitter': '<path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/>',
    }
    c = f' class="{cls}"' if cls else ''
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>')

SOCIAL = [('facebook', 'Facebook'), ('linkedin', 'LinkedIn'), ('twitter', 'Twitter')]
VALUE_ICONS = ['target', 'award', 'globe', 'heart']
SERVICE_ICONS = {'medicalTrade': 'box', 'consulting': 'users', 'premium': 'heart'}
SERVICE_IMAGES = {'medicalTrade': C['images']['service_trade'],
                  'consulting': C['images']['service_consulting'],
                  'premium': C['images']['service_premium']}

def lang_switcher(page, lang, extra_class=''):
    label = next(l['label'] for l in C['languages'] if l['code'] == lang)
    items = ''.join(
        f'<a href="{page_href(page, l["code"], lang)}" class="{"current" if l["code"] == lang else ""}">{l["flag"]} {esc(l["label"])}</a>'
        for l in C['languages'])
    return f'''<div class="lang-switch {extra_class}">
        <button type="button" aria-haspopup="true">{esc(label)}{icon('chevron-down')}</button>
        <div class="dropdown">{items}</div>
      </div>'''

# ---------------- 頁頭 / 頁尾 ----------------
def header(page, lang):
    nav = I18N[lang]['nav']
    logo = asset('img/logo.webp', lang)
    links = ''.join(
        f'<a href="{page_href(p, lang, lang)}" class="{"active" if p == page else ""}">{esc(nav[NAV_KEY[p]])}</a>'
        for p in PAGES)
    mlinks = ''.join(
        f'<a href="{page_href(p, lang, lang)}" class="mnav {"active" if p == page else ""}">{esc(nav[NAV_KEY[p]])}</a>'
        for p in PAGES)
    return f'''<header class="site-header">
  <div class="container">
    <div class="header-inner">
      <a href="{page_href('index', lang, lang)}"><img class="logo" src="{logo}" alt="{esc(C['site_name_en'])}"></a>
      <nav class="main-nav">{links}</nav>
      <div class="header-actions">
        {lang_switcher(page, lang)}
        <button class="menu-toggle" id="menu-toggle" aria-label="Menu">{icon('menu')}</button>
      </div>
    </div>
  </div>
  <div class="mobile-panel" id="mobile-panel">
    <div class="container">
      {mlinks}
      {lang_switcher(page, lang)}
    </div>
  </div>
</header>'''

def footer(page, lang):
    nav = I18N[lang]['nav']
    ft = I18N[lang]['footer']
    ct = I18N[lang]['contact']
    logo = asset('img/logo-footer.webp', lang)
    links = ''.join(
        f'<li><a href="{page_href(p, lang, lang)}">{esc(nav[NAV_KEY[p]])}</a></li>' for p in PAGES)
    social = ''.join(f'<a href="{C["social"][s]}" aria-label="{label}">{icon(s)}</a>' for s, label in SOCIAL)
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <img class="logo" src="{logo}" alt="{esc(C['site_name_en'])}">
        <p class="desc">{esc(t(lang, 'hero', 'subheading'))}</p>
      </div>
      <div>
        <h4>{esc(ft['quickLinks'])}</h4>
        <ul>{links}</ul>
      </div>
      <div>
        <h4>{esc(ft['contactInfo'])}</h4>
        <ul class="footer-contact">
          <li>{icon('map-pin')}<span>{esc(ct['address'])}</span></li>
          <li>{icon('mail')}<a href="mailto:{C['email']}">{C['email']}</a></li>
          <li>{icon('phone')}<a href="{C['whatsapp_link']}">WhatsApp: {C['whatsapp']}</a></li>
        </ul>
        <div class="footer-hours">
          <p class="k">{esc(ft['businessHours'])}</p>
          <p class="v">{esc(ft['businessHoursText'])}</p>
        </div>
      </div>
      <div>
        <h4>{esc(ft['followUs'])}</h4>
        <div class="social-row">{social}</div>
        <div class="footer-lang">{lang_switcher(page, lang)}</div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{esc(ft['copyright'])}</p>
      <div class="links">
        <a href="#">{esc(ft['privacy'])}</a>
        <a href="#">{esc(ft['terms'])}</a>
      </div>
    </div>
  </div>
</footer>'''

def site_name_for(lang):
    if lang == 'zh-CN': return '澳门桥霍顿有限公司'
    if lang == 'zh-TW': return C['site_name']
    return C['site_name_en']

def page_shell(page, lang, title, description, body, body_class=''):
    css = asset('css/style.css', lang)
    js = asset('js/main.js', lang)
    lang_links = ''.join(
        f'<link rel="alternate" hreflang="{l}" href="{abs_url(page, l)}">'
        for l in LANGS)
    canonical = abs_url(page, lang)
    base = C.get('site_url', 'https://bridgeholdengroup.com').rstrip('/')
    og_image = base + '/assets/img/hero-home.webp'
    og_locale = {'zh-TW': 'zh_TW', 'zh-CN': 'zh_CN', 'en': 'en_US', 'pt': 'pt_PT'}[lang]
    site_name = site_name_for(lang)
    jsonld = ''
    if page == 'index':
        jsonld = f'''<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Organization","name":"{site_name}","alternateName":"{C['site_name_en']}","url":"{base}","logo":"{base}/assets/img/logo-footer.webp","email":"{C['email']}"}}
  </script>'''
    bc = f' class="{body_class}"' if body_class else ''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} - {esc(C['site_name_en'])}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(site_name)}">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" type="image/webp" href="{asset('img/logo.webp', lang)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css}">
  <noscript><style>.reveal{{opacity:1 !important;transform:none !important;}}</style></noscript>
  {lang_links}
  {jsonld}
</head>
<body{bc}>
{header(page, lang)}
<main>
{body}
</main>
{footer(page, lang)}
<script src="{js}" defer></script>
</body>
</html>'''

# ---------------- 首頁 ----------------
def render_index(lang):
    hero = I18N[lang]['hero']
    stats = ''.join(f'''
      <div class="stat-card reveal">
        {icon(s['icon'])}
        <div><div class="num">{esc(s['number'])}</div><div class="lbl">{esc(t(lang, 'stats', s['key']))}</div></div>
      </div>''' for s in C['stats'])
    svcs = I18N[lang]['services']
    cards = ''.join(f'''
      <div class="service-card reveal">
        <div class="icon-badge">{icon(SERVICE_ICONS[k])}</div>
        <h3>{esc(svcs[k]['title'])}</h3>
        <p>{esc(svcs[k]['description'])}</p>
        <a class="btn btn-blue" href="{page_href('services', lang, lang)}">{esc(svcs[k]['cta'])}</a>
      </div>''' for k in ['medicalTrade', 'consulting', 'premium'])
    body = f'''
<section class="hero-home">
  <div class="hero-bg"><img src="{asset('img/' + C['images']['hero_home'], lang)}" alt="Professional medical team"></div>
  <div class="hero-content">
    <h1>{esc(hero['tagline'])}</h1>
    <p>{esc(t(lang, 'company', 'description'))}</p>
    <div class="hero-ctas">
      <a class="btn btn-hero-solid" href="{page_href('contact', lang, lang)}">{esc(hero['ctaPrimary'])}</a>
      <a class="btn btn-hero-ghost" href="{page_href('services', lang, lang)}">{esc(hero['ctaSecondary'])}</a>
    </div>
  </div>
</section>
<section class="stats-band">
  <div class="container">
    <div class="grid grid-4">{stats}
    </div>
  </div>
</section>
<section class="section-lg">
  <div class="container">
    <h2 class="section-title center-xl">{esc(svcs['title'])}</h2>
    <div class="grid grid-3">{cards}
    </div>
  </div>
</section>'''
    return page_shell('index', lang, t(lang, 'nav', 'home'), t(lang, 'company', 'description'), body)

# ---------------- 關於我們 ----------------
def render_about(lang):
    ab = I18N[lang]['about']
    competencies = ''.join(f'''
        <div class="competency-card reveal">
          <div class="dot-box"><div class="dot"></div></div>
          <p>{esc(ab[f'competency{i}'])}</p>
        </div>''' for i in range(1, 5))
    values = ''.join(f'''
        <div class="value-card reveal">
          <div class="icon-badge">{icon(VALUE_ICONS[i])}</div>
          <p>{esc(ab[f'value{i+1}'])}</p>
        </div>''' for i in range(4))
    body = f'''
<section class="h-blue-hero">
  <div class="container">
    <h1>{esc(ab['title'])}</h1>
  </div>
</section>
<section class="section about-sec-white">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <h2 class="section-title" style="margin-bottom:1.5rem;">{esc(ab['mission'])}</h2>
        <p style="font-size:1.125rem;color:var(--gray-600);line-height:1.625;">{esc(ab['missionText'])}</p>
      </div>
      <div class="reveal"><img src="{asset('img/' + C['images']['about_mission'], lang)}" alt="Medical team collaboration"></div>
    </div>
  </div>
</section>
<section class="section about-sec-gray">
  <div class="container">
    <h2 class="section-title center">{esc(ab['competencies'])}</h2>
    <div class="grid grid-2">{competencies}
    </div>
  </div>
</section>
<section class="section about-sec-white">
  <div class="container">
    <div class="split">
      <div class="reveal"><img src="{asset('img/' + C['images']['about_presence'], lang)}" alt="Global presence"></div>
      <div class="reveal">
        <h2 class="section-title" style="margin-bottom:1.5rem;">{esc(ab['presence'])}</h2>
        <p style="font-size:1.125rem;color:var(--gray-600);line-height:1.625;">{esc(ab['presenceText'])}</p>
      </div>
    </div>
  </div>
</section>
<section class="section about-sec-gray">
  <div class="container">
    <h2 class="section-title center">{esc(ab['values'])}</h2>
    <div class="grid grid-4">{values}
    </div>
  </div>
</section>'''
    return page_shell('about', lang, ab['title'], ab['missionText'], body)

# ---------------- 服務項目 ----------------
def render_services(lang):
    sp = I18N[lang]['servicesPage']
    rows = ''
    for i, k in enumerate(['medicalTrade', 'consulting', 'premium']):
        s = sp[k]
        benefits = ''.join(f'''
          <div class="item">{icon('check-circle')}<span>{esc(s[f'benefit{j}'])}</span></div>''' for j in range(1, 5))
        text_col = f'''<div class="reveal">
          <div class="svc-icon">{icon(SERVICE_ICONS[k])}</div>
          <h2>{esc(s['title'])}</h2>
          <p class="desc">{esc(s['description'])}</p>
          <div class="svc-benefits">{benefits}
          </div>
          <a class="btn btn-blue" href="{page_href('contact', lang, lang)}">{esc(s['cta'])}</a>
        </div>'''
        img_col = f'''<div class="reveal"><img src="{asset('img/' + SERVICE_IMAGES[k], lang)}" alt="{esc(s['title'])}"></div>'''
        cols = (text_col + img_col) if i % 2 == 0 else (img_col + text_col)
        rows += f'''
      <div class="svc-row split">{cols}
      </div>'''
    body = f'''
<section class="h-blue-hero">
  <div class="container">
    <h1>{esc(sp['title'])}</h1>
  </div>
</section>
<section class="section">
  <div class="container">{rows}
  </div>
</section>'''
    return page_shell('services', lang, sp['title'], sp['title'], body)

# ---------------- 國際顧問委員會 ----------------
def render_advisory(lang):
    ab = I18N[lang]['advisoryBoardNew']
    cats = ''.join(f'''
        <div class="cat-card reveal">
          <h3>{esc(c['name'])}</h3>
          <p>{esc(c['desc'])}</p>
        </div>''' for c in ab['categories'])
    experts = ''.join(f'''
        <div class="expert-card reveal">
          <div class="photo"><img src="{asset('img/' + e['image'], lang)}" alt="{esc(e['name'])}"></div>
          <div class="body">
            <p class="cat">{esc(e['category'])}</p>
            <h3>{esc(e['name'])}</h3>
            <p class="role">{esc(e['title'])}</p>
            <p class="bio">{esc(e['bio'])}</p>
          </div>
        </div>''' for e in ab['experts'])
    steps = ''.join(f'''
        <div class="step-card reveal">
          <div class="num">{i + 1}</div>
          <h4>{esc(s['title'])}</h4>
          <p>{esc(s['desc'])}</p>
        </div>''' for i, s in enumerate(ab['process']['steps']))
    ctas = f'''<a class="btn btn-gold" href="{page_href('contact', lang, lang)}">{esc(ab['hero']['cta1'])}</a>
        <a class="btn btn-gold-outline" href="{page_href('contact', lang, lang)}">{esc(ab['hero']['cta2'])}</a>'''
    body = f'''
<section class="hero-luxury">
  <div class="hero-bg"><img src="{asset('img/' + C['images']['advisory_hero'], lang)}" alt="Premium Medical Facility"></div>
  <div class="container hero-content">
    <h1>{esc(ab['hero']['title'])}</h1>
    <p>{esc(ab['hero']['subtitle'])}</p>
    <div class="hero-ctas">{ctas}</div>
  </div>
</section>
<section class="lux-ivory-sec">
  <div class="container">
    <p class="intro reveal">{esc(ab['about']['description'])}</p>
    <div class="compliance-card reveal">
      <p class="tag">{esc(lbl('complianceNotice', lang))}</p>
      <p>{esc(ab['about']['disclaimer'])}</p>
    </div>
  </div>
</section>
<section class="lux-black-sec">
  <div class="container">
    <div class="grid grid-3">{cats}
    </div>
  </div>
</section>
<section class="lux-navy-sec">
  <div class="container">
    <div class="grid grid-3">{experts}
    </div>
  </div>
</section>
<section class="lux-ivory-sec" style="padding:6rem 0;">
  <div class="container">
    <div class="process-head">
      <h2>{esc(ab['process']['title'])}</h2>
      <div class="bar"></div>
    </div>
    <div class="grid grid-4">{steps}
    </div>
  </div>
</section>
<section class="lux-cta">
  <div class="container">
    <h2>{esc(ab['hero']['title'])}</h2>
    <div class="hero-ctas">{ctas}</div>
  </div>
</section>'''
    desc = {'zh-TW': '由心臟外科、心臟內科及麻醉科國際專家支持的優質跨境醫療諮詢服務',
            'zh-CN': '由心脏外科、心脏内科及麻醉科国际专家支持的优质跨境医疗咨询服务',
            'en': 'Premium cross-border medical advisory services supported by international specialists in cardiac surgery, cardiology, and anesthesiology.',
            'pt': 'Serviços premium de consultoria médica transfronteiriça apoiados por especialistas internacionais em cirurgia cardíaca, cardiologia e anestesiologia.'}[lang]
    return page_shell('advisory-board', lang, ab['hero']['title'], desc, body, body_class='luxury-page')

# ---------------- 成功案例 ----------------
def render_stories(lang):
    ss = I18N[lang]['successStoriesNew']
    def case_card(c):
        return f'''
        <div class="case-card reveal">
          <h3>{esc(c['title'])}</h3>
          <div class="field"><h4>{esc(lbl('caseChallenge', lang))}</h4><p>{esc(c['challenge'])}</p></div>
          <div class="field"><h4>{esc(lbl('caseSolution', lang))}</h4><p>{esc(c['solution'])}</p></div>
          <div class="field"><h4>{esc(lbl('caseOutcome', lang))}</h4><p>{esc(c['outcome'])}</p></div>
          <div class="quote">&ldquo;{esc(c['summary'])}&rdquo;</div>
        </div>'''
    groups = {}
    for cat in ['cardiology', 'surgery']:
        cards = ''.join(case_card(c) for c in ss['cases'] if c['category'] == cat)
        groups[cat] = cards
    body = f'''
<section class="hero-stories">
  <div class="container hero-content">
    <h1>{esc(ss['hero']['title'])}</h1>
    <p>{esc(ss['hero']['subtitle'])}</p>
  </div>
</section>
<div class="disclaimer-bar"><p>{esc(ss['disclaimer'])}</p></div>
<section class="stories-sec">
  <div class="container" data-tabs>
    <div class="story-tabs">
      <button type="button" data-tab="cardiology" class="active">🫀 {esc(ss['categories']['cardiology'])}</button>
      <button type="button" data-tab="surgery">❤️ {esc(ss['categories']['surgery'])}</button>
    </div>
    <div data-pane="cardiology" class="active"><div class="grid grid-3">{groups['cardiology']}
    </div></div>
    <div data-pane="surgery"><div class="grid grid-3">{groups['surgery']}
    </div></div>
  </div>
</section>
<section class="stories-cta">
  <div class="container">
    <h2>{esc(ss['hero']['title'])}</h2>
    <div class="hero-ctas">
      <a class="btn btn-gold" href="{page_href('contact', lang, lang)}">{esc(ss['cta']['btn1'])}</a>
      <a class="btn btn-gold-outline" href="{page_href('contact', lang, lang)}">{esc(ss['cta']['btn2'])}</a>
    </div>
  </div>
</section>'''
    desc = {'zh-TW': '國際心臟專家支持的心臟內科與心臟外科真實成功案例',
            'zh-CN': '国际心脏专家支持的心脏内科与心脏外科真实成功案例',
            'en': 'Real-world clinical success cases supported by international cardiac specialists across cardiology and cardiac surgery.',
            'pt': 'Casos clínicos de sucesso reais apoiados por especialistas cardíacos internacionais em cardiologia e cirurgia cardíaca.'}[lang]
    return page_shell('success-stories', lang, ss['hero']['title'], desc, body)

# ---------------- 聯絡我們 ----------------
def render_contact(lang):
    ct = I18N[lang]['contact']
    err_req, err_email = esc(lbl('errRequired', lang)), esc(lbl('errEmail', lang))
    opts = ''.join(f'<option value="{k}">{esc(v)}</option>' for k, v in ct['serviceTypes'].items())
    def field(fid, label, ftype='text', required=False, extra=''):
        req = ' *' if required else ''
        reqattr = ' required' if required else ''
        return f'''<div class="form-group">
            <label for="{fid}">{esc(label)}{req}</label>
            {extra if extra else f'<input id="{fid}" name="{fid}" type="{ftype}"{reqattr}>'}
            <p class="err"></p>
          </div>'''
    contact_form = f'''<form class="ajax-form" data-err-required="{err_req}" data-err-email="{err_email}" data-submitting="{esc(ct['submitting'])}" novalidate>
          {field('name', ct['name'], required=True)}
          {field('company', ct['company'])}
          {field('country', ct['country'])}
          {field('phone', ct['phone'], 'tel', required=True)}
          {field('email', ct['email'], 'email', required=True)}
          <div class="form-group">
            <label for="message">{esc(ct['message'])} *</label>
            <textarea id="message" name="message" rows="4" required></textarea>
            <p class="err"></p>
          </div>
          <button type="submit" class="btn btn-blue form-submit">{esc(ct['submit'])}</button>
          <div class="form-toast">{icon('check')}{esc(ct['successMessage'])}</div>
        </form>'''
    consult_form = f'''<form class="ajax-form" data-err-required="{err_req}" data-err-email="{err_email}" data-submitting="{esc(ct['submitting'])}" novalidate>
          {field('c-name', ct['name'], required=True)}
          {field('c-email', ct['email'], 'email', required=True)}
          <div class="form-group">
            <label for="serviceType">{esc(ct['serviceType'])} *</label>
            <select id="serviceType" name="serviceType" required>
              <option value="">{esc(ct['serviceType'])}</option>
              {opts}
            </select>
            <p class="err"></p>
          </div>
          {field('preferredTime', ct['preferredTime'], 'datetime-local')}
          <div class="form-group">
            <label for="additionalNotes">{esc(ct['additionalNotes'])}</label>
            <textarea id="additionalNotes" name="additionalNotes" rows="4"></textarea>
            <p class="err"></p>
          </div>
          <button type="submit" class="btn btn-blue form-submit">{esc(ct['submit'])}</button>
          <div class="form-toast">{icon('check')}{esc(ct['successMessage'])}</div>
        </form>'''
    info_rows = f'''
          <div class="info-row">
            <div class="icon-badge">{icon('map-pin')}</div>
            <div><p class="k">{esc(lbl('address', lang))}</p><p class="v">{esc(ct['address'])}</p></div>
          </div>
          <div class="info-row">
            <div class="icon-badge">{icon('mail')}</div>
            <div><p class="k">{esc(lbl('email', lang))}</p><a class="v" href="mailto:{C['email']}">{C['email']}</a></div>
          </div>
          <div class="info-row">
            <div class="icon-badge">{icon('phone')}</div>
            <div><p class="k">WhatsApp</p><a class="v" href="{C['whatsapp_link']}">{C['whatsapp']}</a></div>
          </div>
          <div class="info-row">
            <div class="icon-badge">{icon('clock')}</div>
            <div><p class="k">{esc(ct['businessHours'])}</p><p class="v">{esc(ct['businessHoursText'])}</p></div>
          </div>'''
    body = f'''
<section class="h-blue-hero">
  <div class="container">
    <h1>{esc(ct['title'])}</h1>
    <p>{esc(ct['subtitle'])}</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div data-tabs>
        <div class="form-tabs">
          <button type="button" data-tab="contact" class="active">{esc(ct['contactForm'])}</button>
          <button type="button" data-tab="consultation">{esc(ct['consultationForm'])}</button>
        </div>
        <div class="form-card active" data-pane="contact">
          {contact_form}
        </div>
        <div class="form-card" data-pane="consultation">
          {consult_form}
        </div>
      </div>
      <div>
        <div class="info-card reveal">
          <h3>{esc(ct['companyInfo'])}</h3>
          {info_rows}
        </div>
      </div>
    </div>
  </div>
</section>'''
    return page_shell('contact', lang, ct['title'], ct['subtitle'], body)

# ---------------- 構建 ----------------
RENDERERS = {'index': render_index, 'about': render_about, 'services': render_services,
             'advisory-board': render_advisory, 'success-stories': render_stories,
             'contact': render_contact}

def build():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(DIST, 'assets'))
    with open(os.path.join(DIST, 'CNAME'), 'w') as f:
        f.write(C.get('site_url', 'https://bridgeholdengroup.com').replace('https://', '').replace('http://', '').strip('/') + '\n')

    base = C.get('site_url', 'https://bridgeholdengroup.com').rstrip('/')
    with open(os.path.join(DIST, 'robots.txt'), 'w') as f:
        f.write(f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n')

    # 404 頁（GitHub Pages 自動使用根目錄 404.html）
    not_found_body = f'''
<section class="nf-hero">
  <div class="container">
    <h1>404</h1>
    <p>{esc(lbl('notFound', DEFAULT))}</p>
    <a class="btn btn-blue" href="index.html">{esc(lbl('backHome', DEFAULT))}</a>
  </div>
</section>'''
    with open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8') as f:
        f.write(page_shell('index', DEFAULT, '404', 'Page not found', not_found_body))

    count = 2
    urls = []
    for lang in LANGS:
        outdir = DIST if lang == DEFAULT else os.path.join(DIST, lang)
        os.makedirs(outdir, exist_ok=True)
        for page in PAGES:
            html_out = RENDERERS[page](lang)
            name = 'index.html' if page == 'index' else f'{page}.html'
            with open(os.path.join(outdir, name), 'w', encoding='utf-8') as f:
                f.write(html_out)
            urls.append((page, lang))
            count += 1

    # sitemap.xml（含 hreflang alternates）
    xhtml = 'xmlns:xhtml="http://www.w3.org/1999/xhtml"'
    items = []
    for page, lang in urls:
        loc = abs_url(page, lang)
        alts = ''.join(
            f'\n      <xhtml:link rel="alternate" hreflang="{l}" href="{abs_url(page, l)}"/>'
            for l in LANGS)
        items.append(f'''  <url>
      <loc>{loc}</loc>{alts}
      <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(page, DEFAULT)}"/>
  </url>''')
    with open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" {xhtml}>\n'
                + '\n'.join(items) + '\n</urlset>\n')
    print(f'OK: generated {count} files -> {DIST}')

if __name__ == '__main__':
    build()
