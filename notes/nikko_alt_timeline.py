# 9/17–18 日光替代版時間軸試算（2026-09-14 依使用者提案）
# 第一天：東照宮 → 華嚴瀑布 → 旅館湖邊耍廢；第二天：頭班船 → 大使館別墅 → 回旅館拿行李下山
# 輸入：官方遊覽船時刻表（chuzenjiko-cruise.com/timetable.html，※ 印 4/20–11/4 運航）
#       船の駅中禅寺 → 20 分 → 菖蒲ヶ浜 → 20 分 → 大使館別荘記念公園 → 10 分 → 立木観音 → 5 分 → 船の駅
from datetime import datetime, timedelta
def T(s): return datetime(2026,9,17,*map(int,s.split(':')))
def add(t,m): return t+timedelta(minutes=m)
def f(t): return t.strftime('%H:%M')

print('=== 9/17（四）東照宮 + 華嚴瀑布 ===')
t=T('09:39'); print(f(t),'東武日光著')
t=add(t,26); print(f(t),'ヤマト空手便＋巴士案內所買フリーパス完成，搭巴士')
t=add(t,10); print(f(t),'西参道下車')
t=add(t,5);  toshogu_in=t; print(f(t),'東照宮入場')
t=add(t,85); print(f(t),'東照宮參拜完（陽明門、眠貓、奧宮 約 85 分）')
t=add(t,10); print(f(t),'湯波午餐入店')
t=add(t,65); print(f(t),'午餐結束，走到神橋／西参道站牌')
t=T('13:00'); print(f(t),'巴士上伊呂波坂')
t=add(t,40); print(f(t),'中禪寺溫泉巴士站著')
t=add(t,5);  print(f(t),'華嚴瀑布電梯（營業 8:00–17:00）')
t=add(t,40); print(f(t),'看完瀑布（含排隊約 40 分）')
t=add(t,15); print(f(t),'步行到なごみ（約 15 分）')
print('15:00 なごみ check-in 開始（標準 15:00–18:00）; 空手便最晚 17:00 送達')
print('  → 瀑布後到 check-in 之間空檔約', (T('15:00')-t).seconds//60, '分；瀑布若排隊 1 小時也不影響')

print()
print('=== 9/18（五）遊湖 + 大使館別墅 ===')
D=datetime(2026,9,18)
def T2(s): return datetime(2026,9,18,*map(int,s.split(':')))
seg=[('船の駅中禅寺',0),('菖蒲ヶ浜',20),('大使館別荘記念公園',20),('立木観音',10),('船の駅中禅寺',5)]
def loop(dep):
    out=[];t=dep
    for name,m in seg:
        t=add(t,m); out.append((name,t))
    return out
for dep in ['09:00','10:00','11:00']:
    print(dep,'發 →',' / '.join(f'{n} {f(t)}' for n,t in loop(T2(dep))[1:]))

BUS_LEAVE=T2('13:15'); TRAIN=T2('14:57')
print()
print('情境 A：碼頭正常停靠，09:00 頭班船到大使館下船')
a=loop(T2('09:00')); arr=[t for n,t in a if n=='大使館別荘記念公園'][0]
print(f(arr),'大使館碼頭下船，步行 5 分 → 英國大使館別墅（9:00 開園）')
re1=[t for n,t in loop(T2('10:00')) if n=='大使館別荘記念公園'][0]
re2=[t for n,t in loop(T2('11:00')) if n=='大使館別荘記念公園'][0]
back1=loop(T2('10:00'))[-1][1]; back2=loop(T2('11:00'))[-1][1]
print(f'  大使館停留 {(re1-arr).seconds//60} 分 → {f(re1)} 上 10:00 班次 → {f(back1)} 回船の駅（離 13:15 巴士還有 {(BUS_LEAVE-back1).seconds//60} 分）')
print(f'  大使館停留 {(re2-arr).seconds//60} 分 → {f(re2)} 上 11:00 班次 → {f(back2)} 回船の駅（離 13:15 巴士還有 {(BUS_LEAVE-back2).seconds//60} 分）')

print()
print('情境 B：水位低、碼頭臨時通過（官方目前公告狀態），船只能坐一圈不下船')
b=loop(T2('09:00'))[-1][1]; print(f(b),'09:00 班次一圈回船の駅（不停靠）')
w=add(b,35); print(f(w),'湖畔步行約 35 分到英國大使館別墅')
w2=add(w,60); print(f(w2),'停留 60 分（含二樓茶室）')
w3=add(w2,35); print(f(w3),'步行回溫泉街（離 13:15 巴士還有',(BUS_LEAVE-w3).seconds//60,'分：午餐＋取行李）')

print()
print('情境 C：改搭 10:00 班次（早餐吃完再出門），碼頭正常')
c=loop(T2('10:00')); arr=[t for n,t in c if n=='大使館別荘記念公園'][0]
re=[t for n,t in loop(T2('11:00')) if n=='大使館別荘記念公園'][0]; back=loop(T2('11:00'))[-1][1]
print(f'{f(arr)} 大使館下船，停留 {(re-arr).seconds//60} 分，{f(re)} 上 11:00 班次，{f(back)} 回船の駅，離 13:15 巴士 {(BUS_LEAVE-back).seconds//60} 分')

print()
print('下山硬限制：13:15 巴士 → 約 50 分 →', f(add(BUS_LEAVE,50)), '東武日光；14:57 特急，緩衝', (TRAIN-add(BUS_LEAVE,50)).seconds//60, '分')
