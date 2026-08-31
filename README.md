# 東京 2026 · 9/16 作戰

2026/09/15–21 東京行的行前工具站。核心是 9/16 寶可夢卡「30th CELEBRATION」
發售日的搶購作戰表：37 站、三個時段、Pokédex 進度追蹤。

原生 HTML/CSS/JS，無 build step。

## 本機預覽

```bash
python3 -m http.server 8000
# http://localhost:8000
```

不能直接用 `file://` 開，`data/stops.js` 會被 CORS 擋掉。

## 部署到 GitHub Pages

```bash
git init && git add -A && git commit -m "init"
git remote add origin git@github.com:<你的帳號>/tokyo-2026.git
git push -u origin main
```

到 repo 的 **Settings → Pages → Source** 選 **GitHub Actions**，
`.github/workflows/pages.yml` 會自動把整個 repo 推上去。

或者不用 Actions：Source 選 **Deploy from a branch → main / (root)**，
然後把 `pages.yml` 刪掉即可。

網址會是 `https://<帳號>.github.io/tokyo-2026/`。
所有路徑都是相對路徑，放在子目錄下不會壞。

## PWA

支援加入主畫面（iOS：分享 → 加入主畫面）。同源檔案走網路優先，
改 `data/stops.js` 推上去後線上永遠拿到最新版；斷線時退回快取，
路上沒訊號也能看路線、勾站點。

## 外部相依

| 服務 | 用途 | 掛掉的話 |
|---|---|---|
| Google Fonts | M PLUS Rounded 1c、DotGothic16 | 退回系統字體 |
| PokéAPI | 圖鑑 001–037 的名字 | 不顯示名字，其餘正常 |
| PokeAPI/sprites (raw.githubusercontent) | 圖鑑 sprite | 圖隱藏，其餘正常 |

三個都有 try/catch 或 `onerror`，掛掉不會影響勾選與路線功能。

## 要改內容

只動 `data/stops.js`。格式與各欄位意義見 `CLAUDE.md`。
