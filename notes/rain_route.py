# 雨天備案路線計算（2026-09-13）。輸入 notes/rain_candidates.json（Google Maps 抓的候選店）。
# 步行：直線距離 ×1.3（棋盤街廓）、雨天 65 m/min、每店停留 2 分。
# P1：07:00 起，Lawson 優先（全部 Lawson 先跑完，再 7-11＋NewDays），從飯店出發、終點自由。
# P2：09:55 起全家，從飯店出發（中場回飯店擦乾）、終點自由。
import json,math,itertools,io,sys
sys.stdout.reconfigure(encoding='utf-8')
HOTEL=(35.7048331,139.772273)
SPEED=65.0; DWELL=2.0; DETOUR=1.3
C=json.load(io.open('notes/rain_candidates.json',encoding='utf-8'))
EXCL={"ローソン 上野御徒町店"}  # Google 無營業時間、僅 1 則評論，未驗證
def hav(a,b):
    la1,lo1=map(math.radians,a);la2,lo2=map(math.radians,b)
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371000*math.asin(math.sqrt(h))
def walk(a,b): return hav(a,b)*DETOUR
def ll(r): return (r['lat'],r['lng'])
def best_path(start,items):
    """從 start 出發、走完 items（≤9 用全排列窮舉）、終點自由。回傳 (距離, 順序)"""
    best=(1e18,None)
    for perm in itertools.permutations(items):
        d=0;p=start
        for r in perm:
            d+=walk(p,ll(r));p=ll(r)
            if d>=best[0]:break
        if d<best[0]:best=(d,perm)
    return best
def held_karp(start,items):
    """終點自由的開放 TSP，Held-Karp DP。"""
    n=len(items);pos=[ll(r) for r in items]
    D=[[walk(pos[i],pos[j]) for j in range(n)] for i in range(n)]
    S=[walk(start,pos[i]) for i in range(n)]
    INF=1e18;dp={};par={}
    for i in range(n):dp[(1<<i,i)]=S[i];par[(1<<i,i)]=-1
    for mask in range(1,1<<n):
        for j in range(n):
            if not (mask>>j)&1 or (mask,j) not in dp:continue
            base=dp[(mask,j)]
            for k in range(n):
                if (mask>>k)&1:continue
                nm=mask|(1<<k);v=base+D[j][k]
                if v<dp.get((nm,k),INF):dp[(nm,k)]=v;par[(nm,k)]=j
    full=(1<<n)-1
    j=min(range(n),key=lambda j:dp[(full,j)]);d=dp[(full,j)]
    order=[];mask=full
    while j!=-1:
        order.append(items[j]);pj=par[(mask,j)];mask^=(1<<j);j=pj
    return d,order[::-1]
def sched(start_min,order,start=HOTEL):
    t=start_min;p=start;out=[]
    for r in order:
        leg=walk(p,ll(r));t+=leg/SPEED;out.append((t,round(leg),r));t+=DWELL;p=ll(r)
    return out
def fmt(m): return f'{int(m)//60:02d}:{int(m)%60:02d}'
def show(title,rows,total):
    print(f'\n== {title}  總步行 {round(total)} m ==')
    for t,leg,r in rows: print(f'{fmt(t)}  +{leg:4d}m  {r["brand"]:8s} {r["name"]}')

# ---- P1 ----
law=[r for r in C if r['brand']=='lawson' and r['name'] not in EXCL]
sev=[r for r in C if r['brand']=='seven']
nd=[r for r in C if r['name'] in ('NewDays 御徒町南口','NewDays 御徒町北口')]
pool=sorted(law+sev,key=lambda r:r['d_hotel'])[:12]
print('P1 候選（最近 12 家 Lawson/7-11 + 御徒町 NewDays×2）:')
for r in pool+nd: print(f'  {r["d_hotel"]:4d}m {r["brand"]:7s} {r["name"]}')
L=[r for r in pool if r['brand']=='lawson'];R=[r for r in pool if r['brand']=='seven']+nd
# 嚴格版：Lawson 全部先
best=(1e18,None)
for perm in itertools.permutations(L):
    d=0;p=HOTEL
    for r in perm: d+=walk(p,ll(r));p=ll(r)
    if d>=best[0]:continue
    d2,o2=held_karp(p,R)
    if d+d2<best[0]:best=(d+d2,list(perm)+o2)
strict=best
# 放寬版：只固定前 4 家是 Lawson，其餘自由
best=(1e18,None)
for perm in itertools.permutations(L,4):
    d=0;p=HOTEL
    for r in perm: d+=walk(p,ll(r));p=ll(r)
    rest=[r for r in pool+nd if r not in perm]
    d2,o2=held_karp(p,rest)
    if d+d2<best[0]:best=(d+d2,list(perm)+o2)
relaxed=best
s1=sched(7*60-walk(HOTEL,ll(strict[1][0]))/SPEED,strict[1]);show('P1 嚴格（Lawson 全部先）',s1,strict[0])
s2=sched(7*60-walk(HOTEL,ll(relaxed[1][0]))/SPEED,relaxed[1]);show('P1 放寬（前 4 家 Lawson）',s2,relaxed[0])
# ---- P2 ----
fam=[r for r in C if r['brand']=='famima']
fpool=sorted(fam,key=lambda r:r['d_hotel'])[:11]
d,o=held_karp(HOTEL,fpool)
s3=sched(9*60+55-walk(HOTEL,ll(o[0]))/SPEED,o);show('P2 全家 11 家',s3,d)
# 加碼候選（P1 沒收進來、離飯店 ≤ 650m 的 Lawson/7-11）
print('\n加碼候選:')
for r in sorted(law+sev,key=lambda r:r['d_hotel']):
    if r not in pool and r['d_hotel']<=650: print(f'  {r["d_hotel"]:4d}m {r["brand"]:7s} {r["name"]}')
json.dump({'p1_strict':[r['name'] for r in strict[1]],'p1_relaxed':[r['name'] for r in relaxed[1]],'p2':[r['name'] for r in o],
           'p1_strict_m':round(strict[0]),'p1_relaxed_m':round(relaxed[0]),'p2_m':round(d)},io.open('notes/rain_route_out.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
