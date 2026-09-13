# 把 rain_route2.py 的結果寫進 data/stops.js：RAIN_P1／RAIN_P2 兩個陣列＋COORDS 補座標。
# 備註文字在這裡維護；要改路線就改 rain_route2.py 重跑後再跑這支。
import json,io,sys
sys.stdout.reconfigure(encoding='utf-8')
C={r['name']:r for r in json.load(io.open('notes/rain_candidates.json',encoding='utf-8'))}
O=json.load(io.open('notes/rain_route_out.json',encoding='utf-8'))
NOTE={
"ローソン 末広町駅前店":"06:52 出飯店往南 250m，銀座線末広町站旁。07:00 第一發給 Lawson，前四家全是 Lawson",
"ローソン 秋葉原中央通店":"距上一站 80m，同在中央通り上。單店最多進 9 盒，配額全連鎖最高",
"ローソン 上野五丁目店":"往東北 330m，飯店東側。Lawson 第 3 家",
"ローソン 上野中央通店":"回中央通り，飯店北側 100m。Lawson 四連發到此結束",
"セブン-イレブン 上野1丁目店":"距飯店 60m。7-11 各店上架 07:00–10:00 不一，沒貨就走、別等",
"セブン-イレブン 外神田４丁目店":"沿中央通り往南 350m，末広町站一帶",
"ローソン 上野五丁目昭和通店":"往東到昭和通り。第 5 家 Lawson，07:35 還有貨就是賺到",
"セブン-イレブン 台東２丁目店":"昭和通り東側，距上一站 170m",
"セブン-イレブン 仲御徒町駅前店":"往北 300m，日比谷線仲御徒町站上方",
"NewDays 御徒町南口":"JR 御徒町站南口剪票口外，平日 06:50 開。限購 5 包、通勤客不搶卡",
"ローソン 御徒町駅南口店":"距上一站 60m，站前",
"ローソン 御徒町駅北口店":"沿高架往北 90m 到北口。第 7 家、最後一家 Lawson",
"NewDays 御徒町北口":"北口剪票口外，平日 06:30 開。原本 P2 的收尾店，雨天提前收",
"セブン-イレブン 上野２丁目中央通り店":"往西北 250m 回中央通り。收工：御徒町一帶吃早餐、回飯店擦乾換襪子",
"ファミリーマート 湯島三丁目店":"09:45 出飯店往西北 300m。全家多數 10:00 才開賣，09:55 站門口等",
"ファミリーマート 湯島駅前店":"往北 200m，千代田線湯島站前",
"ファミリーマート 文京湯島春日通り店":"距上一站 100m，春日通り上",
"ファミリーマート 上野六丁目南店":"沿春日通り往東 540m，過中央通り、穿 JR 高架下。P2 最長一段",
"ファミリーマート 仲御徒町店":"往南 200m，仲御徒町站一帶",
"ファミリーマート 御徒町ぱんだ広場店":"JR 御徒町站南口 ぱんだ広場 旁。07:00–23:00",
"ファミリーマート 上野三丁目店":"距上一站 100m，往西南",
"ファミリーマート 外神田四丁目蔵前橋通り店":"沿中央通り往南 500m 到蔵前橋通り口",
"ファミリーマート 外神田四丁目店":"往西 150m",
"ファミリーマート 外神田三丁目東店":"往南 120m",
"ファミリーマート 外神田一丁目店":"電気街口一帶，收尾。就地午餐，13:00 前從秋葉原搭總武線去錦糸町",
}
def row(name,eta,mark=None):
    r=C[name];x=[eta,name,r['brand'],NOTE[name],r['cid']]
    if mark:x.append(mark)
    return '['+','.join(json.dumps(v,ensure_ascii=False) for v in x)+']'
p1=[row(n,t,'flag' if i==len(O['p1'])-1 else None) for i,(n,t) in enumerate(zip(O['p1'],O['p1_eta']))]
p2=[row(n,t) for n,t in zip(O['p2'],O['p2_eta'])]
block=('// ---- 雨天備案（步行版）----\n'
'// 9/16 下雨不能騎車時用：路跑頁「☔ 雨天備案」切換後，上午兩段換成這兩個陣列（P3 不變）。\n'
'// 全部門市在飯店 400m（P1）／600m（P2）內，2026-09-13 從 Google Maps 網頁版搜尋抓、座標與 cid 直接取自搜尋結果。\n'
'// 順序用 notes/rain_route2.py 算（直線×1.3、雨天 65 m/min、每店 2 分）：P1 總步行 '+str(O['p1_m'])+' m、P2 '+str(O['p2_m'])+' m。\n'
'// 備註文字在 notes/gen_rain.py，改路線請改 script 重跑，不要手改。\n'
'const RAIN_P1=[\n'+',\n'.join(p1)+'\n];\nconst RAIN_P2=[\n'+',\n'.join(p2)+'\n];\n\n')
p='data/stops.js';s=io.open(p,encoding='utf-8').read()
a='// 飯店座標：9/16 地圖的 H 圖釘、9/21 的起終點\n'
assert s.count(a)==1 and 'RAIN_P1' not in s
s=s.replace(a,block+a)
# COORDS
seen=set()
for i,line in enumerate(s.split('\n')):
    if line.startswith('"') and '":"' in line:seen.add(line.split('"')[1])
lines=[]
for n,t in list(zip(O['p1'],O['p1_eta']))+list(zip(O['p2'],O['p2_eta'])):
    r=C[n]
    if r['cid'] in seen:continue
    seen.add(r['cid']);lines.append('"'+r['cid']+'":"'+str(r['lat'])+','+str(r['lng'])+'", // ☔ '+t+' '+n)
tail='"35.7007345,139.7717177"  // 19:50 ドン・キホーテ 秋葉原\n};'
assert s.count(tail)==1
s=s.replace(tail,'"35.7007345,139.7717177", // 19:50 ドン・キホーテ 秋葉原\n// 雨天備案門市（RAIN_P1／RAIN_P2），2026-09-13 取自 Google Maps 搜尋結果（notes/rain_candidates.py）\n'+'\n'.join(lines).rstrip(',')+'\n};')
# 最後一行不能有逗號
s=s.replace(lines[-1]+'\n};',lines[-1].replace('", //','"  //',1)+'\n};')
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('RAIN_P1',len(p1),'RAIN_P2',len(p2),'COORDS +',len(lines))
