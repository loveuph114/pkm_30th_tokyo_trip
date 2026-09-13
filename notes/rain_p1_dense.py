# 雨天步行版 P1 重排（2026-09-13）：不限定原單車路線的門市，從 notes/kanda_candidates.json
# （神田／日本橋／小川町／小伝馬町／岩本町一帶的 Lawson・7-11・NewDays）挑一條密集順路的步行線。
# 條件：
# - 起點：銀座線 神田駅（06:40 末広町上車、06:45 到），第一站 07:00 到；前 2 站必須是 Lawson（07:00 全國同步開賣）。
# - 終點錨點：ファミリーマート 神田須田町二丁目店（P2 09:55 起手店），不計入站數，但路線要收在它附近。
# - 站數 N=14（與單車版 P1 相同）；步行 65 m/min、每店 2 分、直線×1.3。
# - 已在單車版 COORDS 裡的店沿用原 cid 與原店名（Google 改過名的：神田駅西口ビル店＝西口通り店、神田須田町一丁目店＝万世橋南店）。
# 演算法：枚舉前 2 家 Lawson 的順序（限 神田駅 700m 內的 Lawson），其餘 12 家用「最便宜插入」建路線，
# 再做 2-opt 與「換一家」局部改善，取「總步行＋長段罰分」最小者（單段超過 350m 的部分加倍計，避免長段）。
import json, math, io, sys, itertools
sys.stdout.reconfigure(encoding='utf-8')

SPEED, DWELL, DET, N = 65.0, 2.0, 1.3, 14
KANDA = (35.6917, 139.7708)        # JR／銀座線 神田駅
END = (35.6959298, 139.7719519)    # ファミリーマート 神田須田町二丁目店
C = json.load(io.open('notes/kanda_candidates.json', encoding='utf-8'))['stores']
ORIG = json.load(io.open('notes/orig_route.json', encoding='utf-8'))
ORIG_BY_CID = {d[4]: d for d in ORIG['P1'] + ORIG['P2']}


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def w(a, b):
    return hav(a, b) * DET


stores = []
for b, n, la, lo, hx, st in C:
    cid = str(int(hx, 16))
    if cid in ORIG_BY_CID:
        n = ORIG_BY_CID[cid][1]
    stores.append({'brand': b, 'name': n, 'll': (la, lo), 'cid': cid, 'status': st, 'd_kanda': hav(KANDA, (la, lo))})
# 太遠的不考慮（離神田駅 >1100m）
EXCL = {'ローソン 大手町フィナンシャルシティグランキューブ店',  # 大手町辦公大樓內店型、非 24h，不確定有進卡
        'NewDays 神田北口'}  # 與 神田南口改札外 同一站，NewDays 限購 5 包、留一家就好
pool = [s for s in stores if s['d_kanda'] <= 1100 and s['name'] not in EXCL]
laws = [s for s in pool if s['brand'] == 'lawson' and s['d_kanda'] <= 700]
print(f'候選 {len(pool)} 家（神田駅 1100m 內），其中 700m 內 Lawson {len(laws)} 家')


MAXLEG = 350  # 超過這個長度的單段，超出部分加倍計價（避免像 6→7 那種一走好幾分鐘的段）


def path_len(seq, start, end, pen=True):
    d = 0
    p = start
    for s in seq:
        leg = w(p, s['ll'])
        d += leg + (2 * max(0, leg - MAXLEG) if pen else 0)
        p = s['ll']
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
    """最便宜插入建 k 站路線，再 2-opt，再嘗試換站。"""
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


# 前 2 站固定 Lawson（單車版也是 07:00、07:05 兩家 Lawson），之後自由
overall = None
for duo in itertools.permutations(laws, 2):
    d0 = path_len(list(duo), KANDA, duo[1]['ll']) - w(duo[1]['ll'], duo[1]['ll'])
    if d0 > 900:
        continue
    rest = [s for s in pool if s not in duo]
    seq, d = build(duo[1]['ll'], END, rest, N - 2)
    tot = d0 + d
    if overall is None or tot < overall[0]:
        overall = (tot, list(duo) + seq)
        print(f'  更好：加權 {round(tot)} m  {" → ".join(s["name"][:12] for s in duo)} …')

_, route = overall
tot = path_len(route, KANDA, END, pen=False)
t = 7 * 60 - w(KANDA, route[0]['ll']) / SPEED
p = KANDA
rows = []
print(f'\n== 步行版 P1 {N} 站  總步行 {round(tot)} m（含神田駅→第一站、最後一站→須田町二丁目全家）==')
print(f'  06:{int(t) % 60:02d} 神田駅出發（步行 {round(w(KANDA, route[0]["ll"]))} m 到第一站）')
for s in route:
    leg = w(p, s['ll'])
    t += leg / SPEED
    rows.append({'eta': f'{int(t) // 60:02d}:{int(t) % 60:02d}', 'leg': round(leg), **{k: s[k] for k in ('brand', 'name', 'cid', 'status')}, 'lat': s['ll'][0], 'lng': s['ll'][1]})
    print(f'  {rows[-1]["eta"]} +{round(leg):4d}m  {s["brand"]:8s} {s["name"]}  {s["status"]}')
    t += DWELL
    p = s['ll']
print(f'  收尾 → 須田町二丁目全家 {round(w(p, END))} m')
json.dump({'route': rows, 'total_m': round(tot)}, io.open('notes/rain_p1_dense_out.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
