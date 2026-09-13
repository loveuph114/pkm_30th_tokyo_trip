# 把 rain_prune.py 的結果（notes/rain_prune_out.json）寫進 data/stops.js 的 RAIN_P1／RAIN_P2。
# 門市就是單車版 P1／P2 的子集合（同 cid、同順序），只換時間與備註；座標沿用 COORDS，不用補。
# 備註在這裡維護；要改砍站規則改 rain_prune.py 重跑後再跑這支。
import json,io,re,sys
sys.stdout.reconfigure(encoding='utf-8')
O=json.load(io.open('notes/rain_prune_out.json',encoding='utf-8'))
NOTE={
"ローソン 内神田三丁目店":"06:40 銀座線 末広町 → 神田（2 站），西口出來走 1–2 分；不搭車就 06:28 出門走 2.1 km。06:55 到位，07:00 第一發給 Lawson",
"ローソン 内神田二丁目店":"距上一站 170m。單店最多進 9 盒，配額全連鎖最高",
"セブン-イレブン 神田駅西口ビル店":"在地下一樓，找電梯／樓梯多抓 1 分鐘",
"セブン-イレブン 千代田鍛冶町一丁目店":"穿過神田站到東側。過這站看錶，落後就直接跳去岩本町",
"セブン-イレブン 日本橋室町三丁目店":"三越前一帶，24 小時",
"ローソン 日本橋本町二丁目店":"純商辦區 Lawson，這一區最值得抓的一家。雨天版最南端，接著北上",
"セブン-イレブン 千代田岩本町一丁目店":"沿昭和通り正北 730m，一條直線。雨天版最長一段",
"セブン-イレブン 神田岩本町店":"秋葉原邊緣大型店，07:00 開門",
"NewDays メッツ秋葉原":"限購 5 包、通勤客不搶卡。在剪票口外。收工：秋葉原站吃早餐，或回飯店擦乾",
"ファミリーマート 神田須田町二丁目店":"09:50 從秋葉原出發往南 330m。全家多數 10:00 才開賣，09:55 站門口等",
"ファミリーマート 神田鍛冶町三丁目店":"往南 280m。平日 24 小時",
"ファミリーマート 岩本町一丁目店":"往東南 600m 到昭和通り側",
"ファミリーマート 新日本橋駅前店":"沿昭和通り往南 350m，JR 新日本橋站上方",
"ファミリーマート 日本橋本町店":"距上一站 200m，同一條路往南",
"ファミリーマート 八重洲さくら通り店":"往南 1 km 過日本橋川，雨天版最長一段。DX 在 340m 外，10:49 到、進高島屋躲雨等 12:00 整理券",
}
def row(d,eta):
    x=[eta,d[1],d[2],NOTE[d[1]],d[4]]+([d[5]] if len(d)>5 and d[5]=='star' else [])
    return '['+','.join(json.dumps(v,ensure_ascii=False) for v in x)+']'
p1=[row(d,t) for d,t,_ in O['p1']];p2=[row(d,t) for d,t,_ in O['p2']]
block=('// ---- 雨天備案（步行版）----\n'
'// 9/16 下雨不能騎車時用：路跑頁「☔ 雨天備案」切換後，上午兩段換成這兩個陣列（P3 不變）。\n'
'// 門市＝單車版 P1／P2 的子集合、原順序不動，只砍繞遠的站（notes/rain_prune.py：每站繞路成本 >250m 就砍，\n'
'// MINISTOP 三家不在優先連鎖直接砍，Lawson 不砍；P2 終點設 JR 浅草橋駅、收完搭總武線去錦糸町）。\n'
'// 步行 65 m/min、每店 2 分：P1 總步行 '+str(O['p1_m'])+' m、P2 '+str(O['p2_m'])+' m。備註文字在 notes/gen_rain.py，不要手改。\n'
'const RAIN_P1=[\n'+',\n'.join(p1)+'\n];\nconst RAIN_P2=[\n'+',\n'.join(p2)+'\n];\n\n')
p='data/stops.js';s=io.open(p,encoding='utf-8').read()
s=re.sub(r'// ---- 雨天備案（步行版）----\n.*?const RAIN_P2=\[\n.*?\n\];\n\n',block,s,count=1,flags=re.S)
assert s.count('const RAIN_P1=')==1
# 拿掉上一版補進 COORDS 的雨天門市座標（這版全部沿用單車版的）
NL=chr(10);s=NL.join(l for l in s.split(NL) if '雨天備案門市' not in l and '// ☔' not in l)
s=s.replace('"35.7007345,139.7717177", // 19:50 ドン・キホーテ 秋葉原\n};','"35.7007345,139.7717177"  // 19:50 ドン・キホーテ 秋葉原\n};')
assert '// ☔' not in s
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('RAIN_P1',len(p1),'RAIN_P2',len(p2))
