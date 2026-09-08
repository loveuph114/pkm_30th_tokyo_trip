# 從 data/stops.js 抽出 P1/P2/P3 每站的地圖連結，輸出 JSON 給瀏覽器解析座標用
import re, json
src = open('data/stops.js', encoding='utf-8').read()
out = []
for phase in ('P1', 'P2', 'P3'):
    block = re.search(r'const %s=\[(.*?)\n\];' % phase, src, re.S).group(1)
    for m in re.finditer(r'^\["([^"]+)","([^"]+)","([^"]+)","[^"]*","([^"]+)"', block, re.M):
        t, name, brand, link = m.groups()
        url = ('https://maps.google.com/?cid=' + link) if link.isdigit() else link
        out.append({'phase': phase, 'time': t, 'name': name, 'url': url})
json.dump(out, open('notes/links.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'stops')
for i, o in enumerate(out): print(i, o['phase'], o['name'], o['url'])
