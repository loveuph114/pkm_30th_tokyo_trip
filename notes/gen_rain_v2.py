# 把雨天備案（茅場町版）寫進 data/stops.js 的 RAIN_P1／RAIN_P2，並補 COORDS。
# 來源：notes/kayabacho_plan.py 的結果（notes/kayabacho_plan_out.json）。
# 備註文字在這裡維護；要改路線改 kayabacho_plan.py 重跑後再跑這支。
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

O = json.load(io.open('notes/kayabacho_plan_out.json', encoding='utf-8'))
NOTE = {
    "ローソン 日本橋茅場町一丁目店": "06:35 出飯店走 350m 到日比谷線仲御徒町，直達茅場町（4 站、約 9 分）。出站 140m，07:00 第一發給 Lawson",
    "ローソン 日本橋茅場町店": "距上一站 200m。單店最多進 9 盒，配額全連鎖最高",
    "セブン-イレブン 日本橋茅場町2丁目店": "距上一站 80m。7-11 各店上架 07:00–10:00 不一，沒貨就走、別等",
    "セブン-イレブン 八丁堀１丁目店": "往南 250m",
    "ローソン 八丁堀二丁目店": "距上一站 100m。第 3 家 Lawson",
    "セブン-イレブン 八丁堀２丁目店": "往西 320m",
    "セブン-イレブン 京橋１丁目店": "往西北 400m，本段最長",
    "セブン-イレブン 日本橋兜町店": "往東北 370m，07:00 開",
    "ローソン 日本橋かぶと町店": "往北 270m。第 4 家 Lawson",
    "セブン-イレブン 兜町東証前店": "往東 310m，東京證交所前",
    "ローソン 日本橋蛎殻町一丁目店": "往東北 360m，07:00 開。第 5 家 Lawson",
    "セブン-イレブン 日本橋人形町３丁目店": "往北 300m",
    "セブン-イレブン 人形町駅西店": "距上一站 120m",
    "ローソン 人形町駅前店": "距上一站 90m。第 6 家 Lawson。收工：人形町吃早餐（甘酒横丁一帶），09:55 前回到 50m 外的全家人形町三丁目店",
    "ファミリーマート 日本橋人形町三丁目店": "P2 起手店，離 Lawson 人形町駅前 50m。全家多數 10:00 才開賣，09:55 站門口等",
    "ファミリーマート 日本橋小学校前店": "往東南 270m",
    "ファミリーマート 水天宮前店": "往東南 230m，水天宮旁",
    "ファミリーマート 京王プレッソイン茅場町店": "往西南 690m 回茅場町，本段最長",
    "ファミリーマート KABUTO ONE店": "往西 260m，兜町 KABUTO ONE 大樓內，06:00 開",
    "ファミリーマート 日本橋三丁目店": "往西 490m，07:00 開。收尾：DX 就在 60m 外，10:37 到、進高島屋 S.C. 東館 5F 等 12:00 整理券",
}


def js(x):
    return '[' + ','.join(json.dumps(v, ensure_ascii=False) for v in x) + ']'


p1 = [js([r['eta'], r['name'], r['brand'], NOTE[r['name']], r['cid']]) for r in O['p1']]
p2 = [js([r['eta'], r['name'], r['brand'], NOTE[r['name']], r['cid']]) for r in O['p2']]
block = ('// ---- 雨天備案（步行版・茅場町）----\n'
         '// 9/16 下雨不能騎車時用：路跑頁「☔ 雨天備案」切換後，上午兩段換成這兩個陣列（P3 不變）。\n'
         '// 不沿用單車版門市：日比谷線 仲御徒町 → 茅場町 直達，P1 在茅場町／八丁堀／兜町／人形町（Lawson 密度是神田的三倍），\n'
         '// P2 全家從人形町往西收到 DX 門口（12:00 整理券）。候選 notes/kayabacho_candidates.json（Google Maps 搜尋抓），\n'
         '// 順序 notes/kayabacho_plan.py（前 2 站 Lawson、最便宜插入＋2-opt＋換站、單段超過 350m 加倍罰分）。\n'
         '// 步行 65 m/min、每店 2 分：P1 ' + str(O['p1_m']) + ' m、P2 ' + str(O['p2_m']) + ' m。備註文字在 notes/gen_rain_v2.py，不要手改。\n'
         'const RAIN_P1=[\n' + ',\n'.join(p1) + '\n];\nconst RAIN_P2=[\n' + ',\n'.join(p2) + '\n];\n\n')

path = 'data/stops.js'
s = io.open(path, encoding='utf-8').read()
a = s.index('// ---- 雨天備案（步行版')
b = s.index('const RAIN_P2=[')
b = s.index('\n];\n', b) + len('\n];\n')
while s[b] == '\n':
    b += 1
s = s[:a] + block + s[b:]
assert s.count('const RAIN_P1=') == 1 and s.count('const RAIN_P2=') == 1

# COORDS：先清掉上一版補的 ☔ 行，再接在 DX 全家那組後面
NL = chr(10)
s = NL.join(l for l in s.split(NL) if '// ☔' not in l and '雨天備案 P1 門市' not in l and '雨天備案門市' not in l)
have = set()
for l in s.split(NL):
    if l.startswith('"') and '":"' in l:
        have.add(l.split('"')[1])
anchor = '"16215509843394927837":"35.6813021,139.7716526", // 10:14 ファミリーマート 八重洲さくら通り店\n'
assert s.count(anchor) == 1
lines = ''.join(f'"{r["cid"]}":"{r["lat"]},{r["lng"]}", // ☔ {r["eta"]} {r["name"]}\n' for r in O['p1'] + O['p2'] if r['cid'] not in have)
s = s.replace(anchor, anchor + '// 雨天備案門市（RAIN_P1／RAIN_P2 茅場町版），2026-09-13 取自 Google Maps 搜尋結果（notes/kayabacho_candidates.json）\n' + lines)
io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
print('RAIN_P1', len(p1), 'RAIN_P2', len(p2), 'COORDS +', lines.count(NL))
