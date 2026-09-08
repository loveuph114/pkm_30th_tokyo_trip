# 把 Tabelog 抓下來的原始清單整理成 data/meals.js 的 MEALS 常數
# 輸入：notes/tabelog_dump2_part*.txt（列表，含縮圖）、notes/tabelog_coords.txt（店ID|lat,lng）
# 抓取日：2026-09-08/09。執行：python notes/gen_meals.py
import re, json, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from genre_zh import GENRE_ZH

ROOT = Path(__file__).resolve().parent.parent
RAW = {}
for f in sorted((ROOT / 'notes').glob('tabelog_dump2_part*.txt')):
    key = None
    for line in f.read_text(encoding='utf-8').splitlines():
        if line.startswith('##'):
            key = line[2:].strip()
            if key == 'END': key = None
            elif key not in RAW: RAW[key] = []
        elif line.strip() and key:
            cols = line.split('|')
            if len(cols) >= 8: RAW[key].append(cols)   # 分段倒出時最後一列可能被截斷，略過
# 同一清單若因分段重複出現，用店ID去重
for k, rows in RAW.items():
    seen, out = set(), []
    for r in rows:
        if r[4] in seen: continue
        seen.add(r[4]); out.append(r)
    RAW[k] = out

COORDS = {}
cf = ROOT / 'notes' / 'tabelog_coords.txt'
if cf.exists():
    for line in cf.read_text(encoding='utf-8').splitlines():
        if '|' in line:
            i, ll = line.split('|', 1)
            if ll.strip(): COORDS[i.strip()] = ll.strip()

# 純甜點／咖啡／麵包／酒吧／住宿／賣店：每個類型都落在這集合的店，不算正餐，剔除
EXCL = set('''カフェ 喫茶店 甘味処 かき氷 和菓子 ケーキ パン スイーツ チョコレート 洋菓子 プリン パンケーキ
フルーツパーラー ジェラート・アイスクリーム ソフトクリーム どら焼き 大福 マカロン ジューススタンド コーヒースタンド
バー 中華菓子 肉まん 焼き芋・大学芋 サンドイッチ ベーグル ドーナツ 惣菜・デリ 弁当 ホテル 旅館・民宿 日本酒バー
ワインバー おにぎり かりんとう その他 売店'''.split())

# 9/15 午餐已落選（CLAUDE.md／stops.js 註解），不要再選回來
REJECT_0915 = {'丸五', '青島食堂 秋葉原店', 'ベンガル', '饗くろ喜', 'とんかつ山家 御徒町店'}

MISSING_GENRE = set()
def zh(genre):
    out = []
    for g in genre.split('、'):
        g = g.strip()
        if g in GENRE_ZH: out.append(GENRE_ZH[g])
        else: MISSING_GENRE.add(g); out.append(g)
    return '・'.join(out)

def upper_yen(s):
    """'￥1,000～￥1,999' → 1999；'～￥999' → 999；'￥100,000～' → 100000；'-' → None"""
    if not s or s == '-':
        return None
    nums = [int(n.replace(',', '')) for n in re.findall(r'[\d,]+', s)]
    if not nums:
        return None
    return nums[-1] if '～' in s and not s.endswith('～') else nums[0]

def rows(key, mode, station, pref, cap, min_score=3.5, reject=(), top=None):
    """mode: 'lunch' 用午餐預算欄，'dinner' 用晚餐預算欄。cap：預算上限（日圓），None 不限"""
    out = []
    for r in RAW[key][:top]:
        name, score, dist, genre, rid = r[0], float(r[1]), r[2], r[3], r[4]
        dinner, lunch = r[5], r[6]
        imgs = [u for u in r[7].split(',') if u and 'nophoto' not in u] if len(r) > 7 else []
        budget = lunch if mode == 'lunch' else dinner
        if score < min_score or name in reject:
            continue
        gs = [g.strip() for g in genre.split('、')]
        if all(g in EXCL for g in gs):
            continue
        u = upper_yen(budget)
        if cap and u and u > cap:
            continue
        where = (station + ' ' + dist + 'm') if dist.isdigit() else station
        url = 'https://tabelog.com/%s/A0000/A000000/%s/' % (pref, rid)
        out.append((rid, [name, zh(genre), r[1], where, budget if budget != '-' else '預算不明', url, COORDS.get(rid, ''), imgs]))
    return out

def merge(*lists):
    seen, out = set(), []
    for lst in lists:
        for rid, row in lst:
            if rid in seen: continue
            seen.add(rid); out.append(row)
    out.sort(key=lambda x: -float(x[2]))
    return out

L, D = 'lunch', 'dinner'
MEALS = {}
def slot(date, kind, note, *lists):
    MEALS.setdefault(date, {})[kind] = {'note': note, 'list': merge(*lists)}

slot('9/15', L, '末広町駅 500m · 昼～¥3,000 · 3.5+ · 週二定休未逐店確認，選定前用 Google 確認營業中',
     rows('suehirocho_lunch', L, '末広町駅', 'tokyo', 3000, reject=REJECT_0915))
slot('9/15', D, '日本橋駅／秋葉原駅 500m · 夜～¥6,000 · 3.5+',
     rows('nihonbashi_dinner', D, '日本橋駅', 'tokyo', 6000), rows('akiba_dinner', D, '秋葉原駅', 'tokyo', 6000))
slot('9/16', L, '秋葉原駅 500m · 昼～¥3,000 · 3.5+', rows('akiba_lunch', L, '秋葉原駅', 'tokyo', 3000))
slot('9/16', D, '秋葉原駅 500m · 夜～¥6,000 · 3.5+ · 20:30 才吃，先看打烊時間', rows('akiba_dinner', D, '秋葉原駅', 'tokyo', 6000))
slot('9/17', L, '日光全區（東照宮周邊到東武日光駅）· 昼～¥5,000 · 3.5+ · 湯波料理店多在 3.5 以下，名單裡是全區高分店',
     rows('nikko_lunch', L, '日光市街', 'tochigi', 5000))
slot('9/17', D, '中禅寺湖周辺 · 山區店少、評價人數少，放寬到 3.0 以上 · 夜～¥6,000 · 18:30 前入店',
     rows('chuzenji_all', D, '中禅寺温泉', 'tochigi', 6000, min_score=3.0))
slot('9/18', L, '中禅寺湖周辺 · 放寬到 3.0 以上（同 9/17 晚餐）· 昼～¥3,000',
     rows('chuzenji_all', L, '中禅寺温泉', 'tochigi', 3000, min_score=3.0))
slot('9/18', D, '上野駅 500m · 夜～¥6,000 · 3.5+ · 與朋友聚餐參考用',
     rows('ueno_dinner', D, '上野駅', 'tokyo', 6000))
slot('9/19', L, '東池袋駅（Sunshine City）500m · 昼～¥3,000 · 3.5+',
     rows('ikebukuro_lunch', L, '東池袋駅', 'tokyo', 3000))
slot('9/19', D, '中野駅／秋葉原駅 500m · 夜～¥6,000 · 3.5+',
     rows('nakano_dinner', D, '中野駅', 'tokyo', 6000), rows('akiba_dinner', D, '秋葉原駅', 'tokyo', 6000))
slot('9/20', L, '秋葉原駅 500m · 昼～¥3,000 · 3.5+', rows('akiba_lunch', L, '秋葉原駅', 'tokyo', 3000))
slot('9/20', D, '元町・中華街駅／みなとみらい駅 500m · 夜～¥6,000 · 3.5+',
     rows('chinatown_dinner', D, '元町・中華街駅', 'kanagawa', 6000), rows('minatomirai_dinner', D, 'みなとみらい駅', 'kanagawa', 6000))
slot('9/21', L, '秋葉原駅 500m · 昼～¥3,000 · 3.5+ · 敬老之日，假日營業另確認',
     rows('akiba_lunch', L, '秋葉原駅', 'tokyo', 3000))
slot('9/21', D, '東京駅／銀座駅 500m · 夜～¥6,000 · 3.5+ · 17:15 早吃，各站只取前 70 名',
     rows('tokyo_dinner', D, '東京駅', 'tokyo', 6000, top=70), rows('ginza_dinner', D, '銀座駅', 'tokyo', 6000, top=70))

def js_rows(lst):
    return ',\n'.join('  ' + json.dumps(r, ensure_ascii=False) for r in lst)

buf = io.StringIO()
buf.write('// MEALS：每天午餐／晚餐口袋名單（由 notes/gen_meals.py 從 Tabelog 抓取結果產生，抓取日 2026-09-08）\n')
buf.write('// 每列：[店名, 類型（中文）, 食べログ分數, 距離（以搜尋車站為圓心）, 預算, Tabelog 連結, "lat,lng"（空字串＝沒座標）, [縮圖路徑…]]\n')
buf.write('// 縮圖路徑接在 app.js 的 MEAL_IMG（tblg.k-img.com）後面直接外連，不存 repo\n')
buf.write('// 條件：車站 500m、依評分排序、只收 3.5 以上（中禅寺湖放寬到 3.0）、剔除純咖啡／甜點／麵包／酒吧店\n')
buf.write('// 定休日與當天是否營業「未」逐店確認，選定前照慣例用 Google Maps 看營業中。要改條件請改 gen_meals.py 重跑，不要手改這個檔。\n')
buf.write('const MEALS={\n')
for date, kinds in MEALS.items():
    buf.write('"%s":{\n' % date)
    for kind in ('lunch', 'dinner'):
        if kind not in kinds: continue
        k = kinds[kind]
        buf.write(' %s:{note:%s,list:[\n%s\n ]},\n' % (kind, json.dumps(k['note'], ensure_ascii=False), js_rows(k['list'])))
    buf.write('},\n')
buf.write('};\n')
(ROOT / 'data' / 'meals.js').write_text(buf.getvalue(), encoding='utf-8')

nocoord = 0
for date, kinds in MEALS.items():
    print(date, {k: (len(v['list']), sum(1 for r in v['list'] if not r[6])) for k, v in kinds.items()}, '(家數, 缺座標)')
    nocoord += sum(1 for v in kinds.values() for r in v['list'] if not r[6])
print('lists loaded:', {k: len(v) for k, v in RAW.items()})
print('coords:', len(COORDS), 'rows without coords:', nocoord)
if MISSING_GENRE: print('未翻譯類型:', ' / '.join(sorted(MISSING_GENRE)))
