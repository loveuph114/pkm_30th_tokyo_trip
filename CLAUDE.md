# CLAUDE.md

給 Claude Code 的專案脈絡。**動路線之前先讀完「路線決策」那一節。**

## 這是什麼

2026/09/15–21 東京行的行前工具站。核心是 9/16（三）寶可夢卡「30th CELEBRATION」
全球同步發售當天的搶購作戰表。手機優先，實際使用情境是清晨 6:50 一邊騎共享電動單車
一邊看螢幕。

三個分頁：**路跑**（9/16 全天 36 站）、**行程**（七天）、**情報**（日文、規則、勘查清單）。

## 架構

原生 HTML/CSS/JS，**沒有 build step、沒有框架、沒有套件**。這是刻意的——
GitHub Pages 直接吃靜態檔，改一行就能推。請維持這個狀態。

```
index.html          # 三個 .view 區塊 + 底部分頁
assets/styles.css   # 全部樣式，CSS 變數在 :root
assets/app.js       # 渲染、勾選狀態、倒數、分頁切換、SW 註冊
data/stops.js       # 所有資料（P1/P2/P3/PHRASES/RECON/DAYS/BOOKINGS）
data/meals.js       # 每天午餐／晚餐口袋名單（MEALS）——由 notes/gen_meals.py 產生，不要手改
manifest.webmanifest # PWA 設定（可裝到主畫面）
sw.js               # Service Worker：同源網路優先（資料保鮮）、跨源快取優先（sprite 秒開）
```

**改內容只動 `data/stops.js`。** 那裡是純資料陣列，不需要碰邏輯。

### 雨天備案（步行版・茅場町）

路跑頁 hero 下方的「☔ 雨天備案」鈕：把 `localStorage` 的 `tokyo2026:rain` 設成 `'1'` 後整頁重載，
上午兩段換成 `RAIN_P1`／`RAIN_P2`（P3 不變），`index.html` 裡 `.dry-only`／`.rain-only` 的文字跟著切
（`body.rain`）。勾選 id 加 `r` 前綴（`ra0`、`rb0`），與單車版分開存；P3 的 `c` 兩版共用。兩版都是 14＋6＋12＝32 站。
- **與單車版同一區、不同站數**（單車版後來也搬到茅場町）：日比谷線 仲御徒町 → 茅場町 直達，
  茅場町駅 600m 內 Lawson 5 家（神田駅同範圍只有 3 家），DX 就在茅場町西邊 500m。
- 候選 `notes/kayabacho_candidates.json`（2026-09-13 Google Maps 抓，人形町／茅場町為中心，排除辦公大樓內店型），
  另有 `notes/kanda_candidates.json`（神田一帶，前一版用的，留著備查）。`notes/kayabacho_plan.py` 以茅場町駅為起點、
  前 2 站固定 Lawson，最便宜插入＋2-opt＋換站挑 14 家（單段超過 350m 的部分加倍罰分）；P2 從 P1 終點出發、
  終點 DX，挑 6 家全家。結果 P1 3.3 km（Lawson 6 家、最長一段 400m）、P2 2.1 km。
- `notes/gen_rain_v2.py` 把兩者與備註寫進 `stops.js`、補 COORDS。**要改路線改 script 重跑，不要手改。**
- 非 24 小時的店開店時間都查過（蛎殻町 Lawson／兜町 7-11／日本橋三丁目全家 07:00、KABUTO ONE 06:00）；
  有沒有進卡沒逐店確認。沒收進來的候選列在路跑頁第 04 段的雨天版清單，當作「有餘裕就加碼」的順序。

### 地圖點位資料

- `COORDS`：站點地圖連結原文 → `"lat,lng"`。**新增門市要一起補座標**，否則該站不會出現在地圖上
  （console 會警告）。座標用瀏覽器開 cid 連結後，從網址的 `!3d<lat>!4d<lng>` 抄。
- `ROUTES`：9/16 以外每天的點位 `[名稱, "lat,lng"]`，依當天順序排；9/16 由 P1/P2/P3 + `HOTEL`
  自動組成（上午＝飯店＋P1＋P2、下午＝P3），刪站不用改。
- 解析座標用的 script 與原始輸出在 `notes/`。
- 導航不做站內路線按鈕（曾做過、已拿掉）：每列的「導航」鈕（與全螢幕資訊卡的「導航」）直接開 Google Maps 步行導航。
- **資訊卡只在全螢幕時出現。** 一般模式列表就在地圖下方，點圖釘改成「列表捲到那家＋標記」（`p.onTap`）；
  沒有列表的日卡地圖（9/16 以外）沒有 `onTap`，照舊點圖釘開卡。

### 餐廳口袋名單（行程頁日卡「午餐」「晚餐」鈕）

每張日卡標題列有「午餐」「晚餐」兩顆鈕，各開一個全螢幕 dialog（`.mdlg`，第一次開才建，之後重用）：
地圖固定在最上面（橘＝午餐、紫＝晚餐），下面是類型 chip（多選、OR）、排序 chip（預設「近 → 遠（車站）」，
按「距我」會要定位並改依目前位置排）、然後是名單。**圖釘編號＝目前名單順序**（篩選／排序後會重編）。
名單捲動時地圖自動移到目前露出的第一家並標記該圖釘（不開資訊卡）；點名單列開資訊卡；點圖釘把名單捲到那家。
開 dialog 會 `pushState({mdlg:1})`，返回鍵＝關閉；dialog 內再進地圖全螢幕會再疊一筆，返回鍵先退全螢幕再關 dialog。
車站距離從距離字串的公尺數解析，沒數字的（中禅寺温泉／日光市街）排最後、維持評分順序。資料在 `data/meals.js` 的 `MEALS`，
每列 `[店名, 類型（中文）, 分數, 距離, 預算, Tabelog 連結, "lat,lng", [縮圖…]]`。
- 來源是 Tabelog 站點搜尋（2026-09-08 抓）：車站周邊 500m、依評分排、只收 3.5 以上
  （中禅寺湖店少，放寬到 3.0）、午餐預算～¥3,000、晚餐～¥6,000、剔除純咖啡／甜點／麵包／酒吧。
- 座標從各店頁面 JSON-LD 抓（`notes/tabelog_coords.txt`）；縮圖是列表頁的 3 張 320px 方圖，
  路徑存在 meals.js、由 `MEAL_IMG` 前綴直接外連 tblg.k-img.com（已確認不擋外站 referer），圖片不進 repo。
- 類型翻譯表在 `notes/genre_zh.py`，新類型沒對到會在產生時印出「未翻譯類型」。
- 原始抓取結果在 `notes/tabelog_dump2_part1–4.txt`，整理 script 是 `notes/gen_meals.py`。
  **要改條件或換車站，改 script 重跑**，不要手改 meals.js。
- **9/17 午餐是例外：湯波料理優先。** `part4` 的 `nikko_yuba` 是東照宮周邊湯波店（表參道口～神橋），只收 9/17（四）有營業的店，
  距離欄是到東照宮而非車站；`slot(..., by_group=True)` 讓湯波組整組排在全區非湯波備選前面。這組是 2026-09-14 在 Tabelog 被擋、
  Chrome 擴充沒連上時手整理的：分數／預算抄 Google 搜尋結果的食べログ摘要、座標抄 Google 地圖（coords 檔尾有註記）、沒縮圖。
  Chrome 連得上時可照原流程重抓補縮圖，店 ID 已對好。
- 名單只是候選：定休日、當天是否營業都沒逐店查。選定後照舊規則用 Google Maps 確認「營業中」，
  9/15 的最終選擇填回 `stops.js` 的 `LUNCH_0915`。
- Tabelog 連結用 `tabelog.com/{pref}/A0000/A000000/{店ID}/`，區域碼給 0 也能開（已驗證）。
- Tabelog 有 Cloudflare 人機驗證，app 內建瀏覽器與直接抓網頁都會被擋；用 Claude in Chrome
  在真人 Chrome 裡以頁內 fetch 抓列表才行。網址參數：`LstRange=SG`（500m）、`SrtT=rt&Srt=D`（評分排序）、
  `RdoCosTp=2&LstCosT=3`（午餐預算上限 ¥3,000；`RdoCosTp=1` 是晚餐）。

### 內嵌 Google 地圖（Maps JavaScript API）

路跑頁最上方一張（圖釘＝圖鑑編號，灰＝已勾選、紅＝下一站），行程頁每張日卡「📍 地圖」展開一張（第一次展開才建立）。
- **路跑地圖是 sticky 的**（`#runmap-wrap.run-sticky`，是 `.wrap` 的直接子元素、不在 section 裡，sticky 才蓋得到整段清單）：
  往下捲到頂欄下方就貼住，`top` 用 JS 量 `.bar` 高度寫進 `--bar-h`。貼頂後頁面捲動時，找清單裡露出超過一半的第一站，
  地圖 pan 過去、切半天、該圖釘加 `.cur`（紅色外圈）；還沒貼頂不跟。「下一站」與清單的「地圖」鈕會用程式捲動，
  期間 `holdFollow` 暫停跟隨，捲停 450ms 後把目標設成目前站（不再 pan）。
- **按鈕全部在地圖下方的工具列 `.map-tools`**（上午／下午 chips、我、下一站、全螢幕），由 `mapControls()` 建在 `.map-inner` 裡；
  全螢幕時 `.map-inner` 變 flex 直排，工具列貼在螢幕底部。只有資訊卡還走 `map.controls`（BOTTOM_CENTER）。
- **API key 不在 repo 裡。** 使用者在 app 的表單貼一次，存 `localStorage` 的 `tokyo2026:gmapkey`。
  沒 key 就顯示表單；key 無效時 `gm_authFailure` 會把表單帶錯誤訊息叫回來。
  「更換／清除 key」在路跑頁地圖區塊下方。key 本身應在 Cloud Console 限制網域
  `loveuph114.github.io` 與 `localhost:8000`。
- 圖釘用 `AdvancedMarkerElement`＋`mapId:'DEMO_MAP_ID'`（Google 的預設樣式 id，不用另建），
  content 是自製的 `.pin` div，狀態變化只改 className，不換元素。
- 要在全螢幕時也看得到的東西，必須是 `.map-inner` 的子孫（工具列）或走 `map.controls`（資訊卡）：
  全螢幕只是 `.map-inner` 鋪滿視窗，外面的東西會被蓋掉。
- 全螢幕是自製的（Google 的 fullscreenControl 關掉）：`.map-inner` 加 `.fs` 用 `position:fixed` 鋪滿視窗，
  **不用 Fullscreen API**——真全螢幕在切到 Google Maps app 再回來時會被瀏覽器退出，且沒有點擊事件不能自動再進去。
  進入時 `pushState` 一筆，返回鍵＝退出全螢幕。工具列用 `env(safe-area-inset-*)`＋固定 36px 推開系統列；
  sticky 容器有自己的 z-index，進全螢幕時會被加 `.fs-host` 抬到 1000，不然會被底部分頁蓋到。
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

P1+P2+P3 共 36 站（18＋6＋12；雨天版 14＋6＋12＝32），依序對應圖鑑編號，`SPRITE(n)` 從 PokeAPI/sprites 取圖。
未勾選是灰剪影，勾選後變彩色。站數改了要一起改 hero 的「上午 N 家超商」與 `index.html` 的 `0/36`。

## 路線決策（重要：這些不是隨便排的）

以下幾點看起來像可以優化的地方，但都是刻意的，**動之前先確認你理解原因**：

1. **整條上午路線在兜町・茅場町・八丁堀・人形町，不在飯店附近。**（2026-09-13 定案，原本是內神田→日本橋→秋葉原）
   原因：茅場町駅 600m 內有 5 家 Lawson，內神田一帶只有 3 家；Lawson 是唯一全國統一 07:00 開賣的連鎖
   （7-11 各店 07:00–10:00 不定），且單店配額最高（上一彈最多 9 盒 vs 7-11 的 6 盒）。這一帶是金融・商辦區
   （兜町有東證），週三早上店裡是通勤族不是卡友。DX 就在茅場町西邊 500m，全家波段收完直接進場用 12:00 整理券。

2. **P1 第 1 站是 かぶと町 Lawson，離飯店 3.5km。** 第一站限定 24 小時店（07:00 才開門的店開門即開賣、沒有緩衝），
   前 2 站固定 Lawson，其餘由 `notes/kayabacho_plan.py bike` 用最便宜插入＋2-opt＋換站算最短，單段超過 600m 加倍罰分。
   06:35 出發沿昭和通り南下。

3. **第 2 站 八丁堀二丁目 Lawson 那段 720m 是全線最長**，是為了讓 Lawson 排前面；之後全部在 100–360m。
   MINISTOP 已不在路線上（該區沒有）。

4. **P2 全部是全家**，因為全家多數分店 10:00 才開賣，跟 P1 的 07:00 波段錯開。
   從 P1 收工點人形町起手，水天宮前折回茅場町、兜町，6 家收到 DX 門口 60m（10:15）。

5. **P3（下午→晚上）不做動線優化。** 時間整體比原案晚 1 小時（DX 之後先回旅館放東西）。 早上要 90 秒一家是因為貨會消失；下午之後是
   「架上有就有」，多繞 200m 沒差。下午走錦糸町非觀光區（總武線一站，四家全在
   站前 500m 內），傍晚回秋葉原逛卡店——卡店整天收購補貨，晚上貨較齊，
   順序按打烊時間排。曾考慮イトーヨーカドー曳舟，因玩具樓層無法確認
   且熱門彈常改抽選販售而捨棄。不要為了縮短 P3 而重排。

6. **門市座標與 cid 全部取自 Google Maps 網頁版搜尋結果**（`notes/kayabacho_candidates.json`，2026-09-13），
   非 24 小時的店逐店查過開店時間。新增門市請照做，不要憑名稱推測——最早的清單有近半是不存在的店名。
   辦公大樓內店型（大廳、地下街、站內小店）貨架小，已排除。**有沒有進卡沒逐店確認**，9/15 勘查要問。

## 待辦

- [ ] 9/15 實地勘查後，把撲空的店從 `data/stops.js` 刪掉
- [ ] 9/17 空手便：出發前跟 旅籠なごみ 說一聲 9/17 會有ヤマト宅急便送隨身包、請代收；當天 14:00 前在東武日光站櫃台交件
      （ヤマト 2026/09/01 版當日手荷物配送表：日光市內・中禅寺・湯元方面 14:00 締切、17:00 前送達）
- [ ] 人形町一帶的共享單車還車點沒查，9/15 勘查時看
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
