# 把 notes/coords_raw.txt（瀏覽器解析出的 37 站座標）合併 notes/links.json，
# 產生 data/stops.js 的 COORDS 區塊（連結原文 → "lat,lng"）
import json, re
links = json.load(open('notes/links.json', encoding='utf-8'))
coords = {}
for line in open('notes/coords_raw.txt', encoding='utf-8'):
    line = line.strip()
    if not line: continue
    idx, title, ll = line.split('|')
    coords[int(idx[1:])] = (title, ll)
assert len(coords) == len(links) == 37, (len(coords), len(links))

src = open('data/stops.js', encoding='utf-8').read()
out = ['// COORDS：地圖連結原文（cid 或 place_id 連結）→ "lat,lng"，給整日路線用。',
       '// 2026-09-08 由 Google Maps 網頁版解析（notes/gen_coords.py）。新增門市時要一起補，否則該站不會出現在路線上。',
       'const COORDS={']
for i, o in enumerate(links):
    m = re.search(r'"%s"' % re.escape(o['url'].replace('https://maps.google.com/?cid=', '')), src)
    key = o['url'].replace('https://maps.google.com/?cid=', '')
    assert m, key
    lat, lng = coords[i][1].split(',')
    # 保留 7 位小數（約 1 cm），不做四捨五入以外的處理
    out.append('"%s":"%s,%s", // %s %s' % (key, lat, lng, o['time'], o['name']))
out[-1] = out[-1].replace('", //', '"  //')
out.append('};')
block = '\n'.join(out)
open('notes/coords_block.js', 'w', encoding='utf-8').write(block + '\n')
print(block.count('\n') + 1, 'lines written to notes/coords_block.js')
