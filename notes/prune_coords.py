# 清掉 data/stops.js COORDS 裡沒有任何清單（P1/P2/P3/RAIN_P1/RAIN_P2）引用的座標行。
# 跑完 gen_bike_kayabacho.py 與 gen_rain_v2.py 之後執行。
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
path = 'data/stops.js'
s = io.open(path, encoding='utf-8').read()
a = s.index('const COORDS={')
b = s.index('\n};', a)
lists = s[:a]
used = set(re.findall(r'\["\d\d:\d\d","[^"]*","[^"]*","[^"]*","([^"]+)"', lists))
head, body, tail = s[:a], s[a:b], s[b:]
kept, dropped = [], []
for l in body.split('\n'):
    if l.startswith('"') and '":"' in l:
        k = l.split('"')[1]
        (kept if k in used else dropped).append(l)
    else:
        kept.append(l)
# 最後一個座標行不能有逗號，其餘要有
idx = [i for i, l in enumerate(kept) if l.startswith('"')]
for n, i in enumerate(idx):
    l = kept[i]
    m = re.match(r'(".*?":".*?")\s*,?\s*(//.*)?$', l)
    kept[i] = m.group(1) + (',' if n < len(idx) - 1 else ' ') + (' ' + m.group(2) if m.group(2) else '')
io.open(path, 'w', encoding='utf-8', newline='\n').write(head + '\n'.join(kept) + tail)
print('kept', len(idx), 'dropped', len(dropped))
for l in dropped:
    print('  -', l.split('//')[-1].strip() if '//' in l else l[:40])
