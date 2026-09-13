# 把雨天備案寫進 data/stops.js 的 RAIN_P1／RAIN_P2，並補 COORDS。
# - RAIN_P1：notes/rain_p1_dense.py 的結果（notes/rain_p1_dense_out.json）——神田站起手、密集順路的步行線
# - RAIN_P2：notes/rain_prune.py 的結果（notes/rain_prune_out.json）——單車版 P2（往 DX）步行時程
# 備註文字在這裡維護；要改路線改上面兩支 script 重跑後再跑這支。
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

P1 = json.load(io.open('notes/rain_p1_dense_out.json', encoding='utf-8'))
P2 = json.load(io.open('notes/rain_prune_out.json', encoding='utf-8'))
NOTE = {
    "ローソン 内神田三丁目店": "06:40 銀座線 末広町 → 神田（2 站），06:56 從神田駅走 240m。06:58 到位，07:00 第一發給 Lawson",
    "ローソン 内神田二丁目店": "距上一站 170m。單店最多進 9 盒，配額全連鎖最高",
    "セブンイレブン 内神田２丁目店": "往南 160m。7-11 各店上架 07:00–10:00 不一，沒貨就走、別等",
    "セブン-イレブン 内神田１丁目店": "往北 160m",
    "セブン-イレブン 神田駅西口ビル店": "往東 190m 回神田站西口。在地下一樓，找電梯／樓梯多抓 1 分鐘",
    "NewDays 神田南口改札外": "穿過車站到南口，剪票口外，平日 06:30 開。限購 5 包、通勤客不搶卡",
    "セブン-イレブン 神田駅南口店": "距上一站 40m，同在南口",
    "セブン-イレブン 千代田鍛冶町一丁目店": "往東 170m，神田站東側。過這站看錶",
    "セブン-イレブン 神田紺屋町店": "往東北 260m",
    "セブン-イレブン 千代田鍛冶町2丁目店": "往西北 320m，回到中央通り",
    "セブン-イレブン 神田須田町中央通り店": "沿中央通り往北 390m，本段最長",
    "セブン-イレブン 神田須田町一丁目店": "往西 180m。原清單「神田万世橋店」的真身",
    "セブン-イレブン 神田淡路町ワテラス店": "往西 240m，淡路町站上方 WATERRAS 內，07:00 開",
    "NewDays 神田万世橋ビル": "往東 250m，07:00 開。收工：秋葉原一帶早餐，09:55 前回須田町二丁目全家（290m）",
    "ファミリーマート 神田須田町二丁目店": "09:50 從秋葉原出發往南 330m。全家多數 10:00 才開賣，09:55 站門口等",
    "ファミリーマート 神田鍛冶町三丁目店": "往南 280m。平日 24 小時",
    "ファミリーマート 岩本町一丁目店": "往東南 600m 到昭和通り側",
    "ファミリーマート 新日本橋駅前店": "沿昭和通り往南 350m，JR 新日本橋站上方",
    "ファミリーマート 日本橋本町店": "距上一站 200m，同一條路往南",
    "ファミリーマート 八重洲さくら通り店": "往南 1 km 過日本橋川，雨天版最長一段。DX 在 340m 外，10:49 到、進高島屋躲雨等 12:00 整理券",
}


def js(x):
    return '[' + ','.join(json.dumps(v, ensure_ascii=False) for v in x) + ']'


p1 = [js([r['eta'], r['name'], r['brand'], NOTE[r['name']], r['cid']]) for r in P1['route']]
p2 = [js([t, d[1], d[2], NOTE[d[1]], d[4]]) for d, t, _ in P2['p2']]
block = ('// ---- 雨天備案（步行版）----\n'
         '// 9/16 下雨不能騎車時用：路跑頁「☔ 雨天備案」切換後，上午兩段換成這兩個陣列（P3 不變）。\n'
         '// P1：不沿用單車版，改為神田站起手、全程在神田站 500m 內的密集步行線（notes/rain_p1_dense.py：\n'
         '//     候選 notes/kanda_candidates.json 由 Google Maps 搜尋抓；前 2 站固定 Lawson、單段超過 350m 加倍罰分，\n'
         '//     收在 P2 起手店旁）。總步行 ' + str(P1['total_m']) + ' m。\n'
         '// P2：與單車版同 6 家、一路往南走到 DX（notes/rain_prune.py 算步行時程）。總步行 ' + str(P2['p2_m']) + ' m。\n'
         '// 步行 65 m/min、每店 2 分。備註文字在 notes/gen_rain_v2.py，不要手改。\n'
         'const RAIN_P1=[\n' + ',\n'.join(p1) + '\n];\nconst RAIN_P2=[\n' + ',\n'.join(p2) + '\n];\n\n')

path = 'data/stops.js'
s = io.open(path, encoding='utf-8').read()
a = s.index('// ---- 雨天備案（步行版）----')
b = s.index('const RAIN_P2=[')
b = s.index('\n];\n', b) + len('\n];\n')
while s[b] == '\n':
    b += 1
s = s[:a] + block + s[b:]
assert s.count('const RAIN_P1=') == 1 and s.count('const RAIN_P2=') == 1

# COORDS：先清掉上一次補的 ☔ 行，再接在 DX 全家那組後面
NL = chr(10)
s = NL.join(l for l in s.split(NL) if '// ☔' not in l and '雨天備案 P1 門市' not in l)
have = set()
for l in s.split(NL):
    if l.startswith('"') and '":"' in l:
        have.add(l.split('"')[1])
anchor = '"16215509843394927837":"35.6813021,139.7716526", // 10:14 ファミリーマート 八重洲さくら通り店\n'
assert s.count(anchor) == 1
lines = ''.join(f'"{r["cid"]}":"{r["lat"]},{r["lng"]}", // ☔ {r["eta"]} {r["name"]}\n' for r in P1['route'] if r['cid'] not in have)
s = s.replace(anchor, anchor + '// 雨天備案 P1 門市（RAIN_P1），2026-09-13 取自 Google Maps 搜尋結果（notes/kanda_candidates.json）\n' + lines)
io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
print('RAIN_P1', len(p1), 'RAIN_P2', len(p2), 'COORDS +', lines.count(NL))
