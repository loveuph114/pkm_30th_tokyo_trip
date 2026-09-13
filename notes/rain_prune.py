# 雨天備案（2026-09-13）：不換區域，沿用單車版 P1／P2 的順序，只砍繞遠的站。
# 輸入 notes/orig_route.json（從 data/stops.js 匯出的 P1/P2/COORDS/HOTEL，見 CLAUDE.md 的指令）。
# 每站的「繞路成本」= d(前一站,它)+d(它,下一站)-d(前一站,下一站)（直線×1.3）。
# 步行 65 m/min、每店 2 分。
# P1：ミニストップ 三家全砍（不在優先連鎖）；其餘繞路 >250m 的砍（Lawson 不砍）。終點自由。
# P2：終點固定 ポケモンセンタートウキョーDX（12:00 整理券，全家一路往南收到 DX），繞路 >250m 的砍。
#     每次砍掉目前繞最遠的一家再重算，直到沒有超標的。
import json, math, io, sys
sys.stdout.reconfigure(encoding='utf-8')

D = json.load(io.open('notes/orig_route.json', encoding='utf-8'))
SPEED = 65.0
DWELL = 2.0
DET = 1.3
DXPOS = (35.6802902, 139.7742695)  # ポケモンセンタートウキョーDX（日本橋高島屋 S.C. 東館）


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def ll(s):
    return tuple(map(float, s.split(',')))


HOTEL = ll(D['HOTEL'][1])


def pos(d):
    return ll(D['COORDS'][d[4]])


def walk(a, b):
    return hav(a, b) * DET


def detours(route, start, end=None):
    out = []
    for i, d in enumerate(route):
        p = start if i == 0 else pos(route[i - 1])
        n = end if i == len(route) - 1 else pos(route[i + 1])
        if n is None:
            out.append(0)
            continue
        out.append(walk(p, pos(d)) + walk(pos(d), n) - walk(p, n))
    return out


def total(route, start):
    t = 0
    p = start
    for d in route:
        t += walk(p, pos(d))
        p = pos(d)
    return t


def sched(route, start, t0):
    t = t0
    p = start
    rows = []
    for d in route:
        leg = walk(p, pos(d))
        t += leg / SPEED
        rows.append((t, round(leg), d))
        t += DWELL
        p = pos(d)
    return rows


def fmt(m):
    return f'{int(m) // 60:02d}:{int(m) % 60:02d}'


def report(title, route, start, end=None):
    det = detours(route, start, end)
    print(f'\n== {title}  總步行 {round(total(route, start))} m ==')
    for d, c in zip(route, det):
        print(f'  繞路 {c:5.0f}m  {d[2]:8s} {d[1]}')


def prune(route, start, end, keep_brand, thr):
    r = [d for d in route if d[2] in ('lawson', 'seven', 'famima', 'newdays')]
    while True:
        det = detours(r, start, end)
        cand = [(c, i) for i, (d, c) in enumerate(zip(r, det)) if c > thr and d[2] != keep_brand]
        if not cand:
            break
        c, i = max(cand)
        print(f'  砍：{r[i][1]}（繞路 {c:.0f}m）')
        r.pop(i)
    return r


report('P1 原順序', D['P1'], HOTEL)
report('P2 原順序', D['P2'], pos(D['P1'][-1]), DXPOS)
print('\n-- P1 砍站 --')
p1 = prune(D['P1'], HOTEL, None, 'lawson', 250)
print('-- P2 砍站 --')
p2 = prune(D['P2'], pos(p1[-1]), DXPOS, None, 250)
report('P1 雨天', p1, HOTEL)
report('P2 雨天', p2, pos(p1[-1]), DXPOS)
print(f'  P2 最後一站 → DX 約 {round(walk(pos(p2[-1]), DXPOS))} m')

s1 = sched(p1, HOTEL, 7 * 60 - walk(HOTEL, pos(p1[0])) / SPEED)
print(f'\nP1 時程（06:{60 - round(walk(HOTEL, pos(p1[0])) / SPEED):02d} 出飯店，步行 {round(walk(HOTEL, pos(p1[0])))} m 到第一站）')
for t, leg, d in s1:
    print(f'  {fmt(t)} +{leg:4d}m {d[1]}')
s2 = sched(p2, pos(p1[-1]), 9 * 60 + 55 - walk(pos(p1[-1]), pos(p2[0])) / SPEED)
print('P2 時程（09:55 就位第一家）')
for t, leg, d in s2:
    print(f'  {fmt(t)} +{leg:4d}m {d[1]}')
tend = s2[-1][0] + DWELL + walk(pos(p2[-1]), DXPOS) / SPEED
print(f'  {fmt(tend)} → DX')

json.dump({'p1': [[d, fmt(t), leg] for t, leg, d in s1], 'p2': [[d, fmt(t), leg] for t, leg, d in s2],
           'p1_m': round(total(p1, HOTEL)), 'p2_m': round(total(p2, pos(p1[-1])))},
          io.open('notes/rain_prune_out.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
