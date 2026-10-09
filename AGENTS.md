# 橋霍頓官網（bridgeholdengroup.com）

澳門橋霍頓有限公司（United Macao Bridge Holden Corporation Limited）官方網站，靜態多語言站（en/繁中/简中/pt），由 Hostinger Horizons React SPA 遷出為純靜態站，參照 MFTEDA 官網項目模式。

## 結構

- `content.json` — 全部網站內容的唯一母本（4 語言）。**更新內容只改這裡**。
  - 頂層：`languages`、`default_lang`（en）、`site_name`/`site_name_en`、`site_url`、`email`、`whatsapp`/`whatsapp_link`、`social`、`stats`（首頁 4 個統計數字：47+/23/12+/89%）、`images`（各頁配圖文件名）。
  - `i18n.{lang}`：每語言的文案，主要節點：`nav`、`hero`（首頁）、`company`、`stats`、`services`（首頁核心服務 3 卡）、`advisoryBoardNew`（顧問委員會頁：hero/about/categories/process/experts 6 位專家）、`successStoriesNew`（成功案例頁：hero/disclaimer/categories/cta/cases，分 cardiology 與 surgery 兩組）、`about`、`servicesPage`、`contact`、`footer`。
- `build.py` — 讀 `content.json` 生成 24 個靜態頁面到 `dist/`（6 頁 × 4 語言），另生成 `CNAME`（bridgeholdengroup.com）、`robots.txt`、`sitemap.xml`（含 hreflang）、`404.html`。語言目錄：**英文在根目錄**（原站默認 en），其他在 `zh-TW/`、`zh-CN/`、`pt/`。頁面：`index/about/services/advisory-board/success-stories/contact`。
- `make_content.py` — 由 `.scrape/i18n.json` 生成 `content.json` 的一次性遷移腳本（平時不用跑）。
- `assets/` — 源頭樣式/腳本/圖片，`build.py` 拷貝進 `dist/`。圖片一律 webp：logo、hero-home、about-mission、about-presence、advisory-hero、service-trade、service-consulting、專家照 6 張（expert-{lemma,lavarra,scorsin,mangini,sirbu,desa}）。
- `dist/` — 生成物，**不要手改**，已被 .gitignore 忽略。
- `.scrape/` — 原 Hostinger Horizons 站點的抓取備份（bundle.js、app.css、i18n.json、原始圖片），已被 .gitignore 忽略，僅作參考。

## 更新流程

1. 改 `content.json`。
2. `python3 build.py`。
3. `git add -A && git commit -m "..." && git push`。
4. GitHub Actions 自動構建部署（`.github/workflows/deploy.yml`），約 1 分鐘後線上生效。

本地預覽：`cd dist && python3 -m http.server 8791`，瀏覽器開 `http://localhost:8791/`。

## 關鍵事實

- 設計：金 #d4af37、navy #0f1419、ivory #f3f2ea、medical-blue #0080ff；字體 Playfair Display（標題）+ DM Sans（正文），Google Fonts CDN。
- 原站硬編碼英文的標籤在遷移版已 4 語言本地化，寫在 `build.py` 的 `LBL` dict（Clinical Challenge/Solution/Outcome、Compliance Notice、Address/Email/WhatsApp/Business Hours、表單按鈕等）；新增這類標籤改 `LBL`。
- 已修復的原站 bug：聯繫郵箱 `mailto:info@umbhc.com` → `bridgeHolden@163.com`；WhatsApp 佔位鏈接 `wa.me/85312345678` → `https://wa.me/85366175570`。
- 兩處 tab 切換（成功案例的 Cardiology/Cardiac Surgery、聯繫頁的兩個表單）由 `assets/js/main.js` 實現（純 JS，無框架）；JS 失效時所有 pane 同時顯示，屬可接受降級。
- 頁面滾動顯現動畫靠 IntersectionObserver；JS 失效時內容直接可見。
- 表單為前端演示（與原站一致），未接後端；如需真正收集留言可接 Formspree 等服務。
- 每頁帶 canonical / Open Graph / Twitter Card 與 hreflang；`content.json` 的 `site_url` 是絕對 URL 基準，換域名時改它（CNAME 也隨之更新）。
- 域名 `bridgeholdengroup.com` 目前指向原 Hostinger 站；切換到 GitHub Pages 需：建倉庫推送 → 倉庫 Settings → Pages 選 GitHub Actions → DNS A 記錄指向 GitHub Pages（185.199.108.153/109.153/110.153/111.153）。
- GitHub 倉庫尚未建立；本機 gh CLI 已登錄 workworkxiaosan 賬號，可用 `gh repo create` 建立後推送。
