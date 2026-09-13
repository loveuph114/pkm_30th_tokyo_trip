# 全家波段（10:00）改往日本橋 DX 方向：候選為 2026-09-13 Google Maps 搜尋「ファミリーマート」
# 在秋葉原～日本橋走廊上的店（座標與 hex id 取自搜尋結果）。起點 NewDays メッツ秋葉原（P1 收尾），終點 DX。
# 步行 65 m/min、每店 2 分；單車 200 m/min、每店 1.5 分。直線×1.3。
import math,itertools,io,sys,json
sys.stdout.reconfigure(encoding='utf-8')
START=('NewDays メッツ秋葉原',(35.6981074,139.7726439))
HOTEL=(35.7048331,139.772273)
DX=('ポケモンセンタートウキョーDX',(35.6802902,139.7742695))
C=[  # 名稱, lat, lng, hex, 營業
 ("ファミリーマート 神田須田町二丁目店",35.6959298,139.7719519,"789f2cd77cf86f86","24h"),
 ("ファミリーマート 岩本町一丁目店",35.6916498,139.7750904,"0","24h"),   # 既有 P2 站（cid 882459833544538222）
 ("ファミリーマート 神田鍛冶町三丁目店",35.6942167,139.7709427,"95c0ac843612d88a","–23:00"),
 ("ファミリーマート 神田西口店",35.6909643,139.769852,"70d43a2d0b148706","24h"),
 ("ファミリーマート 新日本橋駅前店",35.6892772,139.7746243,"6883683519c73085","24h"),
 ("ファミリーマート 日本橋本町店",35.6880208,139.7741122,"e6f45c16fa8c77d3","24h"),
 ("ファミリーマート 八重洲さくら通り店",35.6813021,139.7716526,"e109104a03679cdd","24h"),
 ("ファミリーマート ヤエチカ店",35.6807865,139.7694115,"6d5e4cb953d19455","–23:00"),
]
def hav(a,b):
    la1,lo1=map(math.radians,a);la2,lo2=map(math.radians,b)
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371000*math.asin(math.sqrt(h))
w=lambda a,b:hav(a,b)*1.3
P=[(c[1],c[2]) for c in C]
def best_order(start,end,idx):
    best=(1e18,None)
    for perm in itertools.permutations(idx):
        d=0;p=start
        for i in perm:d+=w(p,P[i]);p=P[i]
        d+=w(p,end)
        if d<best[0]:best=(d,perm)
    return best
def sched(order,start,t0,speed,dwell,end):
    t=t0;p=start;rows=[]
    for i in order:
        leg=w(p,P[i]);t+=leg/speed;rows.append((t,round(leg),C[i][0]));t+=dwell;p=P[i]
    leg=w(p,end);t+=leg/speed;rows.append((t,round(leg),'→ '+DX[0]));return rows
fmt=lambda m:f'{int(m)//60:02d}:{int(m)%60:02d}'
d,order=best_order(START[1],DX[1],range(len(C)))
print(f'全部 {len(C)} 家、終點 DX：總距離 {round(d)} m（直達 {round(w(START[1],DX[1]))} m）')
for i in order:
    k=order.index(i);p=START[1] if k==0 else P[order[k-1]];n=DX[1] if k==len(order)-1 else P[order[k+1]]
    print(f'  繞路 {w(p,P[i])+w(P[i],n)-w(p,n):5.0f}m  {C[i][0]}  {C[i][4]}')
for label,speed,dwell in (('步行（雨天）',65,2),('單車',200,1.5)):
    print(f'\n{label}，09:55 就位第一家：')
    for t,leg,nm in sched(order,START[1],9*60+55-w(START[1],P[order[0]])/speed,speed,dwell,DX[1]):print(f'  {fmt(t)} +{leg:4d}m {nm}')
# 砍掉繞路 >250m 的版本
keep=[i for i in order]
while True:
    d2,o2=best_order(START[1],DX[1],keep);det=[]
    for k,i in enumerate(o2):
        p=START[1] if k==0 else P[o2[k-1]];n=DX[1] if k==len(o2)-1 else P[o2[k+1]]
        det.append((w(p,P[i])+w(P[i],n)-w(p,n),i))
    c,i=max(det)
    if c<=250:break
    print(f'\n砍：{C[i][0]}（繞路 {c:.0f}m）');keep.remove(i)
print(f'\n精簡版 {len(o2)} 家：總距離 {round(d2)} m')
for label,speed,dwell in (('步行（雨天）',65,2),('單車',200,1.5)):
    print(f'{label}：')
    for t,leg,nm in sched(o2,START[1],9*60+55-w(START[1],P[o2[0]])/speed,speed,dwell,DX[1]):print(f'  {fmt(t)} +{leg:4d}m {nm}')
print('\ncid：',{c[0]:str(int(c[3],16)) for c in C if c[3]!='0'})
