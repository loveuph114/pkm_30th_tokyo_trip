# 回答「Lawson 為什麼排不進去」：列神田駅 1.1km 內所有 Lawson 的距離，以及硬插進目前步行 P1 的最便宜插入成本。
import json,math,io,sys
sys.stdout.reconfigure(encoding='utf-8')
C=json.load(io.open('notes/kanda_candidates.json',encoding='utf-8'))['stores']
R=json.load(io.open('notes/rain_p1_dense_out.json',encoding='utf-8'))['route']
KANDA=(35.6917,139.7708);END=(35.6959298,139.7719519)
def hav(a,b):
    la1,lo1=map(math.radians,a);la2,lo2=map(math.radians,b)
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*6371000*math.asin(math.sqrt(h))
w=lambda a,b:hav(a,b)*1.3
pts=[KANDA]+[(r['lat'],r['lng']) for r in R]+[END]
inroute={r['name'] for r in R}
print('神田駅 1.1km 內的 Lawson（直線距離）／插進目前路線最少多走幾公尺：')
rows=[]
for b,n,la,lo,hx,st in C:
    if b!='lawson':continue
    d=hav(KANDA,(la,lo))
    if d>1100:continue
    best=min(w(pts[i],(la,lo))+w((la,lo),pts[i+1])-w(pts[i],pts[i+1]) for i in range(len(pts)-1))
    rows.append((d,n,st,best,n in inroute))
for d,n,st,best,inr in sorted(rows):
    print(f'  {d:5.0f}m  {"已在路線" if inr else f"+{best:4.0f}m":8s}  {n}  {st}')
print('\n同範圍 7-11 家數：',sum(1 for b,n,la,lo,hx,st in C if b=="seven" and hav(KANDA,(la,lo))<=600),'（600m 內）')
print('同範圍 Lawson 家數：',sum(1 for b,n,la,lo,hx,st in C if b=="lawson" and hav(KANDA,(la,lo))<=600),'（600m 內）')
