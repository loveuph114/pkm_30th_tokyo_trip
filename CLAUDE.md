# CLAUDE.md

給 Claude Code 的專案脈絡。**動路線之前先讀完「路線決策」那一節。**

## 這是什麼

2026/09/15–21 東京行的行前工具站。核心是 9/16（三）寶可夢卡「30th CELEBRATION」
全球同步發售當天的搶購作戰表。手機優先，實際使用情境是清晨 6:50 一邊騎共享電動單車
一邊看螢幕。

三個分頁：**路跑**（9/16 全天 37 站）、**行程**（七天）、**情報**（日文、規則、勘查清單）。

## 架構

原生 HTML/CSS/JS，**沒有 build step、沒有框架、沒有套件**。這是刻意的——
GitHub Pages 直接吃靜態檔，改一行就能推。請維持這個狀態。

```
index.html          # 三個 .view 區塊 + 底部分頁
assets/styles.css   # 全部樣式，CSS 變數在 :root
assets/app.js       # 渲染、勾選狀態、倒數、分頁切換、SW 註冊
data/stops.js       # 所有資料（P1/P2/P3/PHRASES/RECON/DAYS/BOOKINGS）
manifest.webmanifest # PWA 設定（可裝到主畫面）
sw.js               # Service Worker：同源網路優先（資料保鮮）、跨源快取優先（sprite 秒開）
```

**改內容只動 `data/stops.js`。** 那裡是純資料陣列，不需要碰邏輯。

### 地圖點位資料

- `COORDS`：站點地圖連結原文 → `"lat,lng"`。**新增門市要一起補座標**，否則該站不會出現在地圖上
  （console 會警告）。座標用瀏覽器開 cid 連結後，從網址的 `!3d<lat>!4d<lng>` 抄。
- `ROUTES`：9/16 以外每天的點位 `[名稱, "lat,lng"]`，依當天順序排；9/16 由 P1/P2/P3 + `HOTEL`
  自動組成（上午＝飯店＋P1＋P2、下午＝P3），刪站不用改。
- 解析座標用的 script 與原始輸出在 `notes/`。
- 導航不做站內路線按鈕（曾做過、已拿掉）：從地圖資訊卡的「導航」開 Google Maps 就好。

### 內嵌 Google 地圖（Maps JavaScript API）

路跑頁最上方一張（上午／下午切換，圖釘＝圖鑑編號，灰＝已勾選、紅＝下一站），
行程頁每張日卡「📍 地圖」展開一張（第一次展開才建立）。
- **API key 不在 repo 裡。** 使用者在 app 的表單貼一次，存 `localStorage` 的 `tokyo2026:gmapkey`。
  沒 key 就顯示表單；key 無效時 `gm_authFailure` 會把表單帶錯誤訊息叫回來。
  「更換／清除 key」在路跑頁地圖區塊下方。key 本身應在 Cloud Console 限制網域
  `loveuph114.github.io` 與 `localhost:8000`。
- 圖釘用 `AdvancedMarkerElement`＋`mapId:'DEMO_MAP_ID'`（Google 的預設樣式 id，不用另建），
  content 是自製的 `.pin` div，狀態變化只改 className，不換元素。
- 地圖上的覆蓋層（上午／下午切換、「我」「下一站」、資訊卡）全部走 `map.controls` 放進地圖內部，
  不要用兄弟節點加 absolute 定位：全螢幕時只會顯示全螢幕元素的子樹，外面的東西會消失。
- 全螢幕是自製的（Google 的 fullscreenControl 關掉）：全螢幕化 `.map-inner` 而非地圖本身，
  地圖鋪滿整個螢幕，只把 UI 元件（切換列、按鈕、資訊卡）用 `env(safe-area-inset-*)` 的邊距推開系統列。
- `sw.js` 對 `maps.*` 與 `*.google.com` 主機直接放行，不進 SW 快取（腳本版本會變、圖磚量大）。
- Google Maps 在背景分頁不會初始化，用瀏覽器面板測試時要把分頁切到前景。

### 資料格式

```js
["07:00", "店名", "brand", "備註", "地圖連結", "mark?"]
```

- `brand` → 決定色標，對應 CSS 的 `.p-{brand}`：
  `lawson` / `seven` / `famima` / `ministop` / `newdays` / `donki` / `kaden` / `kadoshop` / `toy`
- 地圖連結有兩種格式，`stopEl()` 會自動判斷：
  - 超商用 `cid`（純數字字串）→ 組成 `maps.google.com/?cid=`
  - 下午的店用完整 `https://www.google.com/maps/place/?q=place_id:...`
- `mark` 可選：`"flag"`（時間標紅，代表可棄）或 `"star"`（店名加星）

### Pokédex 進度

P1+P2+P3 共 37 站，依序對應圖鑑編號 001–037，`SPRITE(n)` 從 PokeAPI/sprites 取圖。
未勾選是灰剪影，勾選後變彩色。

**#025 皮卡丘剛好落在超商最後一站（P1 14 + P2 11 = 25）**，代表早上收工。
增減 P1/P2 的站數會破壞這個對應，要改的話請一起調整 hero 文案。

## 路線決策（重要：這些不是隨便排的）

以下幾點看起來像可以優化的地方，但都是刻意的，**動之前先確認你理解原因**：

1. **P1 第 1、2 站是兩家 Lawson，不是離飯店最近的店。**
   Lawson 是唯一全國統一 07:00 開賣的連鎖（7-11 各店 07:00–10:00 不定），
   且單店配額最高（上一彈最多 9 盒 vs 7-11 的 6 盒）。07:00 這一發必須給 Lawson。

2. **P1 第 3、4 站往西北繞去兩家 MINISTOP，看起來像繞路。**
   MINISTOP 是穴場連鎖、競爭低。從最西邊那家 Lawson 往西北畫弧再往東南收回，
   是「Lawson 必須排第一」前提下的最短路徑。改成先往東會產生真正的原路折返。

3. **P1 第 7 站（日本橋本石町）確實多繞 400m。** 已驗算過所有含它的排法，
   現行是最短的（1194m vs 1282m vs 1556m）。這是該店地理位置的成本，不是排序錯誤。
   它被列為落後時的第一順位棄店。

4. **P2 全部是全家**，因為全家多數分店 10:00 才開賣，跟 P1 的 07:00 波段錯開。

5. **P3（下午→晚上）不做動線優化。** 早上要 90 秒一家是因為貨會消失；下午之後是
   「架上有就有」，多繞 200m 沒差。下午走錦糸町非觀光區（總武線一站，四家全在
   站前 500m 內），傍晚回秋葉原逛卡店——卡店整天收購補貨，晚上貨較齊，
   順序按打烊時間排。曾考慮イトーヨーカドー曳舟，因玩具樓層無法確認
   且熱門彈常改抽選販售而捨棄。不要為了縮短 P3 而重排。

6. **門市清單全部經 Google Places 驗證過座標與營業時間。**
   新增門市請照做，不要憑名稱推測——原始清單有近半是不存在的店名。

## 待辦

- [ ] 9/15 實地勘查後，把撲空的店從 `data/stops.js` 刪掉
- [ ] 兩家 MINISTOP 的上架時間未知。若現場確認是 07:00，
      可把它們提到 P1 最前面，整條線會變成純西→東單向（更好）
- [ ] 池袋寶可夢中心 Mega Tokyo 8/24 已重開，8/24–31 為 09:00 起店門口發
      時間帶整理券（本人親領、指定時段、可能視人流改自由入場）。
      9 月安排尚未公布，公布後更新 `DAYS` 的 9/19 那筆與行程頁的池袋卡片
- [ ] Android 安裝版 PWA 的系統導覽列在淺色主題下顯示黑色：Chrome 已知限制
      （WebAPK 不吃 theme_color），edge-to-edge 支援 2026/07 起陸續補上。
      本站前置條件已備齊（viewport-fit=cover、safe-area、color-scheme:light），
      不需改動，等使用者手機 Chrome 更新自然修復。不要為此改 display:fullscreen

## 慣例

- 介面文字用台灣繁體中文，店名保留日文原文
- 字體：`M PLUS Rounded 1c`（顯示）、`DotGothic16`（倒數數字）、系統 TC 字體（內文）
- 色彩：近白冷底 + 深藍靛（結構）+ 寶可夢紅（強調），超商識別色只用在色標
- 進度存 `localStorage`，key 是 `tokyo2026:done`
