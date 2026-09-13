# 雨天備案「茅場町版」評估（2026-09-13）：日比谷線 仲御徒町 → 茅場町 直達，P1 在茅場町／兜町／人形町一帶
# （Lawson 密度高），P2 全家從茅場町一路往西收到 DX（DX 在茅場町西邊 500m）。
# 候選：notes/kayabacho_candidates.json。演算法同 rain_p1_dense.py（前 2 站 Lawson、最便宜插入＋2-opt＋換站、長段罰分）。
import json, math, io, sys, itertools
sys.stdout.reconfigure(encoding='utf-8')

SPEED, DWELL, DET, MAXLEG = 65.0, 2.0, 1.3, 350
KAYABA = (35.6799, 139.7800)      # 日比谷線 茅場町駅
DX = (35.6802902, 139.7742695)    # ポケモンセンタートウキョーDX
C = json.load(io.open('notes/kayabacho_candidates.json', encoding='utf-8'))['stores']


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def w(a, b):
    return hav(a, b) * DET


stores = [{'brand': b, 'name': n, 'll': (la, lo), 'cid': str(int(hx, 16)), 'status': st, 'd': hav(KAYABA, (la, lo))} for b, n, la, lo, hx, st in C]
EXCL = {'ローソン 日本橋高島屋三井ビルディング店', 'ローソン メトロス茅場町中央口店'}  # 辦公大樓／站內小店，07:00 才開
pool = [s for s in stores if s['name'] not in EXCL]
print('茅場町駅 600m 內：Lawson', sum(1 for s in pool if s['brand'] == 'lawson' and s['d'] <= 600),
      '家、7-11', sum(1 for s in pool if s['brand'] == 'seven' and s['d'] <= 600), '家、全家', sum(1 for s in pool if s['brand'] == 'famima' and s['d'] <= 600), '家')


def path_len(seq, start, end, pen=True):
    d = 0
    p = start
    for s in seq:
        leg = w(p, s['ll'])
        d += leg + (2 * max(0, leg - MAXLEG) if pen else 0)
        p = s['ll']
    if end is None:
        return d
    leg = w(p, end)
    return d + leg + (2 * max(0, leg - MAXLEG) if pen else 0)


def two_opt(seq, start, end):
    best = path_len(seq, start, end)
    improved = True
    while improved:
        improved = False
        for i in range(len(seq) - 1):
            for j in range(i + 1, len(seq)):
                cand = seq[:i] + seq[i:j + 1][::-1] + seq[j + 1:]
                d = path_len(cand, start, end)
                if d < best - 1e-6:
                    seq, best, improved = cand, d, True
    return seq, best


def build(start, end, cands, k):
    seq = []
    rest = list(cands)
    while len(seq) < k and rest:
        bestc = None
        for s in rest:
            for pos in range(len(seq) + 1):
                cand = seq[:pos] + [s] + seq[pos:]
                d = path_len(cand, start, end)
                if bestc is None or d < bestc[0]:
                    bestc = (d, s, pos)
        d, s, pos = bestc
        seq.insert(pos, s)
        rest.remove(s)
    seq, best = two_opt(seq, start, end)
    improved = True
    while improved:
        improved = False
        for i, s in enumerate(list(seq)):
            for r in list(rest):
                cand = seq[:i] + [r] + seq[i + 1:]
                cand, d = two_opt(cand, start, end)
                if d < best - 1e-6:
                    rest.remove(r)
                    rest.append(s)
                    seq, best, improved = cand, d, True
                    break
            if improved:
                break
    return seq, best


def show(title, route, start, t0, end=None):
    tot = path_len(route, start, end, pen=False)
    print(f'\n== {title}  {len(route)} 站  總步行 {round(tot)} m ==')
    t = t0
    p = start
    rows = []
    for s in route:
        leg = w(p, s['ll'])
        t += leg / SPEED
        eta = f'{int(t) // 60:02d}:{int(t) % 60:02d}'
        rows.append({'eta': eta, 'leg': round(leg), **{k: s[k] for k in ('brand', 'name', 'cid', 'status')}, 'lat': s['ll'][0], 'lng': s['ll'][1]})
        print(f'  {eta} +{round(leg):4d}m  {s["brand"]:8s} {s["name"]}  {s["status"]}')
        t += DWELL
        p = s['ll']
    if end is not None:
        print(f'  {int(t + w(p, end) / SPEED) // 60:02d}:{int(t + w(p, end) / SPEED) % 60:02d} → 終點 {round(w(p, end))} m')
    return rows, round(tot)


# ---- P1：Lawson／7-11，14 站，茅場町駅起、終點自由（早餐就地）----
p1pool = [s for s in pool if s['brand'] in ('lawson', 'seven') and s['d'] <= 900]
laws = [s for s in p1pool if s['brand'] == 'lawson' and s['d'] <= 500]
best = None
for duo in itertools.permutations(laws, 2):
    d0 = w(KAYABA, duo[0]['ll']) + w(duo[0]['ll'], duo[1]['ll'])
    rest = [s for s in p1pool if s not in duo]
    seq, d = build(duo[1]['ll'], None, rest, 12)
    if best is None or d0 + d < best[0]:
        best = (d0 + d, list(duo) + seq)
route1 = best[1]
t0 = 7 * 60 - w(KAYABA, route1[0]['ll']) / SPEED
print(f'\n06:{int(t0) % 60:02d} 茅場町駅出發（步行 {round(w(KAYABA, route1[0]["ll"]))} m 到第一站）')
rows1, tot1 = show('P1 茅場町版', route1, KAYABA, t0)

# ---- P2：全家 6 站，從 P1 終點出發、終點 DX，09:55 就位 ----
p2pool = [s for s in pool if s['brand'] == 'famima']
start2 = route1[-1]['ll']
seq2, _ = build(start2, DX, p2pool, 6)
t0 = 9 * 60 + 55 - w(start2, seq2[0]['ll']) / SPEED
rows2, tot2 = show('P2 茅場町版（→ DX）', seq2, start2, t0, DX)
json.dump({'p1': rows1, 'p1_m': tot1, 'p2': rows2, 'p2_m': tot2}, io.open('notes/kayabacho_plan_out.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
