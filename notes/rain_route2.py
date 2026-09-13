# 雨天備案：子集合最佳化（2026-09-13）。承 rain_route.py 的結論——
# P1 前 4 家固定為飯店 200m 內的 4 家 Lawson（末広町駅前→秋葉原中央通→上野五丁目→上野中央通），
# 御徒町 NewDays×2 固定收進來，剩下 8 家從最近的 10 家 Lawson/7-11 裡挑總步行最短的組合。
# P2 從最近 13 家全家裡挑 11 家。
import json,itertools,io,sys
sys.stdout.reconfigure(encoding='utf-8')
exec(io.open('notes/rain_route.py',encoding='utf-8').read().split('# ---- P1 ----')[0])
law=[r for r in C if r['brand']=='lawson' and r['name'] not in EXCL]
sev=[r for r in C if r['brand']=='seven']
byname={r['name']:r for r in C}
FIX=[byname[n] for n in ['ローソン 末広町駅前店','ローソン 秋葉原中央通店','ローソン 上野五丁目店','ローソン 上野中央通店']]
ND=[byname['NewDays 御徒町南口'],byname['NewDays 御徒町北口']]
rest=[r for r in sorted(law+sev,key=lambda r:r['d_hotel']) if r not in FIX][:10]
d0=0;p=HOTEL
for r in FIX:d0+=walk(p,ll(r));p=ll(r)
best=(1e18,None)
for sub in itertools.combinations(rest,8):
    d,o=held_karp(p,list(sub)+ND)
    if d0+d<best[0]:best=(d0+d,FIX+o)
s=sched(7*60-walk(HOTEL,ll(best[1][0]))/SPEED,best[1]);show('P1 最佳 14 家',s,best[0])
fam=sorted([r for r in C if r['brand']=='famima'],key=lambda r:r['d_hotel'])[:13]
best2=(1e18,None)
for sub in itertools.combinations(fam,11):
    d,o=held_karp(HOTEL,list(sub))
    if d<best2[0]:best2=(d,o)
s2=sched(9*60+55-walk(HOTEL,ll(best2[1][0]))/SPEED,best2[1]);show('P2 最佳 11 家',s2,best2[0])
json.dump({'p1':[r['name'] for r in best[1]],'p1_m':round(best[0]),'p2':[r['name'] for r in best2[1]],'p2_m':round(best2[0]),
  'p1_eta':[fmt(t) for t,_,_ in s],'p2_eta':[fmt(t) for t,_,_ in s2]},io.open('notes/rain_route_out.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
