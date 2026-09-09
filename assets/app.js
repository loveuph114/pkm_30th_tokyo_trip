const ALL=[...P1.map((d,i)=>[d,'a'+i]),...P2.map((d,i)=>[d,'b'+i]),...P3.map((d,i)=>[d,'c'+i])];
const SPRITE=n=>'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/'+n+'.png';
let done=new Set();
const KEY='tokyo2026:done';
let prepDone=new Set();
const PREP_KEY='tokyo2026:prep';
function loadPrep(){
  try{const v=localStorage.getItem(PREP_KEY);if(v)prepDone=new Set(JSON.parse(v));}catch(e){}
}
function savePrep(){
  try{localStorage.setItem(PREP_KEY,JSON.stringify([...prepDone]));}catch(e){}
}

async function loadDex(){
  try{
    const r=await fetch('https://pokeapi.co/api/v2/pokemon?limit=25');
    if(!r.ok) throw new Error('dex');
    const j=await r.json();
    const names={};
    j.results.forEach((p,i)=>names[i+1]=p.name);
    document.querySelectorAll('.dex-name').forEach(el=>{
      const n=+el.dataset.no;
      if(names[n]) el.textContent=names[n];
    });
  }catch(e){ /* 抓不到名字不影響使用，剪影照樣顯示 */ }
}
// GitHub Pages 上沒有 window.storage，改用 localStorage
function loadDone(){
  try{const v=localStorage.getItem(KEY);if(v)done=new Set(JSON.parse(v));}catch(e){}
}
function saveDone(){
  try{localStorage.setItem(KEY,JSON.stringify([...done]));}catch(e){}
}

function stopEl(d,id,no){
  const time=d[0],name=d[1],brand=d[2],note=d[3],cid=d[4],mark=d[5];
  const li=document.createElement('li');
  li.className='stop'+(mark?' '+mark:'')+(done.has(id)?' done':'');
  li.tabIndex=0;li.dataset.id=id;
  li.innerHTML=
    '<div class="stop-time">'+time+'</div>'+
    '<div class="dex">'+
      '<img src="'+SPRITE(no)+'" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">'+
      '<span class="dex-no">'+String(no).padStart(3,'0')+'</span></div>'+
    '<div><div class="stop-name">'+name+'</div>'+
    '<div class="stop-note">'+note+'</div>'+
    '<div class="stop-foot"><span class="pill p-'+brand+'">'+brand+'</span>'+
    '<a class="mapbtn" href="'+(cid.indexOf('http')===0?cid:'https://maps.google.com/?cid='+cid)+'" target="_blank" rel="noopener">開地圖 \u2197</a>'+
    '<button type="button" class="mapbtn locate">'+icon('poke-radar','📍')+'地圖</button>'+
    '<span class="dex-name" data-no="'+no+'"></span></div></div>';
  li.querySelector('a.mapbtn').addEventListener('click',e=>e.stopPropagation());
  li.querySelector('.locate').addEventListener('click',e=>{e.stopPropagation();locateStop(id);});
  const toggle=function(){
    if(done.has(id)){done.delete(id);}else{done.add(id);}
    li.classList.toggle('done');saveDone();updateBar();
  };
  li.addEventListener('click',toggle);
  li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}});
  return li;
}

// 按鈕 leading icon：PokeAPI 道具 sprite，載不到就退回 emoji（同底部分頁作法）
const ITEM=n=>'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/'+n+'.png';
const icon=(n,fb)=>'<span class="ic-s"><img src="'+ITEM(n)+'" alt="" loading="lazy" onerror="this.parentNode.textContent=\''+fb+'\'"></span>';

// ── Google Maps（key 由使用者在 app 裡貼一次，存 localStorage，不進 repo）──
// 圖釘用 AdvancedMarkerElement + DEMO_MAP_ID（Google 提供的預設樣式 map id，不用另建）
const GKEY='tokyo2026:gmapkey';
let gmLib=null;      // Promise → {Map,Marker}
const runMaps=[];    // 路跑地圖的 .gmap 元素，勾選站點時同步更新圖釘
const allMaps=[];    // 所有已建立的地圖（含日卡），定位藍點要畫在每一張
let geoWatch=null,mePos=null;
const isRunDay=()=>new Date().toLocaleDateString('sv-SE',{timeZone:'Asia/Tokyo'})==='2026-09-16';
function toast(msg){
  let t=document.getElementById('toast');
  if(!t){t=document.createElement('div');t.id='toast';document.body.appendChild(t);}
  t.textContent=msg;t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('on'),2600);
}
// 兩點距離（公尺），haversine
function distM(a,b){
  const R=6371000,r=Math.PI/180,dl=(b.lat-a.lat)*r,dn=(b.lng-a.lng)*r;
  const h=Math.sin(dl/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dn/2)**2;
  return 2*R*Math.asin(Math.sqrt(h));
}
const llOf=p=>{const [lat,lng]=p.ll.split(',').map(Number);return {lat,lng};};
// 定位：watchPosition，藍點畫在每張地圖上；cb 只在第一次拿到位置時呼叫
function startGeo(cb){
  if(!navigator.geolocation){toast('這台裝置不支援定位');return;}
  if(geoWatch!==null){if(mePos&&cb)cb();return;}
  document.querySelectorAll('.me-btn').forEach(b=>b.classList.add('on'));
  geoWatch=navigator.geolocation.watchPosition(pos=>{
    mePos={lat:pos.coords.latitude,lng:pos.coords.longitude};
    allMaps.forEach(el=>{const M=el._map;if(!M)return;
      if(!M.me){const d=document.createElement('div');d.className='me';M.me=new M.Marker({map:M.map,position:mePos,content:d,zIndex:20,title:'我的位置'});}
      else M.me.position=mePos;});
    if(cb){cb();cb=null;}
  },err=>{toast('定位失敗：'+(err.code===1?'沒有給定位權限':err.message));geoWatch=null;
    document.querySelectorAll('.me-btn').forEach(b=>b.classList.remove('on'));},
  {enableHighAccuracy:true,maximumAge:5000,timeout:15000});
}
// 下一站：找第一個未勾選的站，切到它所在的半天，取景涵蓋它（有定位時連我一起）
function nextPt(el){
  const M=el._map;if(!M)return null;
  const nxt=ALL.find(x=>!done.has(x[1]));if(!nxt)return null;
  const i=M.pts.findIndex(p=>p.id===nxt[1]);
  return i<0?null:{p:M.pts[i],m:M.markers[i]};
}
function focusNext(el,openCard){
  const M=el._map,n=nextPt(el);if(!M||!n)return false;
  if(el._setHalf)el._setHalf(n.p.half);
  focusOn(el,n.p,n.m,openCard);return true;
}
function focusOn(el,p,m,openCard){
  const M=el._map,t=llOf(p);
  if(mePos){const b=new google.maps.LatLngBounds();b.extend(t);b.extend(mePos);M.map.fitBounds(b,70);}
  else{M.map.panTo(t);if(M.map.getZoom()<16)M.map.setZoom(16);}
  if(openCard)M.card.show(p,m);
}
// 地圖左上角控制鈕：「我」定位、「下一站」聚焦（Google 自己的全螢幕鈕在右上）
function mapControls(el){
  const M=el._map,hasRun=M.pts.some(p=>p.id);
  const ctl=document.createElement('div');ctl.className='map-ctl';
  ctl.innerHTML='<button type="button" class="mctl me-btn'+(geoWatch!==null?' on':'')+'">◎ 我</button>'+(hasRun?'<button type="button" class="mctl nx-btn">▶ 下一站</button>':'');
  M.map.controls[google.maps.ControlPosition.LEFT_TOP].push(ctl);
  ctl.querySelector('.me-btn').addEventListener('click',()=>startGeo(()=>{
    if(hasRun&&focusNext(el))return;
    M.map.panTo(mePos);if(M.map.getZoom()<15)M.map.setZoom(15);
  }));
  const nx=ctl.querySelector('.nx-btn');
  if(nx)nx.addEventListener('click',()=>{if(!focusNext(el,true))toast('全部收工，沒有下一站了');});
}
// 清單 → 地圖：捲到路跑地圖、切半天、開資訊卡
function locateStop(id){
  const sec=document.getElementById('runmap-wrap');
  sec.scrollIntoView({behavior:'smooth',block:'start'});
  const el=runMaps[0],M=el&&el._map;
  if(!M){if(!getKey())toast('先貼上 Google Maps key 才有地圖');return;}
  const i=M.pts.findIndex(p=>p.id===id);if(i<0)return;
  if(el._setHalf)el._setHalf(M.pts[i].half);
  const t=llOf(M.pts[i]);M.map.panTo(t);if(M.map.getZoom()<16)M.map.setZoom(16);
  M.card.show(M.pts[i],M.markers[i]);
}
function getKey(){try{return localStorage.getItem(GKEY)||'';}catch(e){return '';}}
function loadGmaps(){
  if(gmLib)return gmLib;
  const key=getKey();if(!key)return null;
  gmLib=new Promise((res,rej)=>{
    window.__gmInit=()=>Promise.all([google.maps.importLibrary('maps'),google.maps.importLibrary('marker')])
      .then(([m,k])=>res({Map:m.Map,Marker:k.AdvancedMarkerElement})).catch(rej);
    window.gm_authFailure=()=>{
      gmLib=null;
      document.querySelectorAll('.gmap').forEach(el=>keyForm(el,'這把 key 不能用：無效、沒啟用 Maps JavaScript API，或網站限制沒包含這個網址。'));
    };
    const s=document.createElement('script');
    s.src='https://maps.googleapis.com/maps/api/js?key='+encodeURIComponent(key)+'&v=weekly&language=ja&region=JP&loading=async&callback=__gmInit';
    s.onerror=()=>{gmLib=null;rej(new Error('Google Maps 載入失敗，檢查網路後重新整理'));};
    document.head.appendChild(s);
  });
  return gmLib;
}
function keyForm(el,msg){
  el.classList.add('nokey');
  el.innerHTML='<form class="keyform"><p>'+(msg||'貼上 Google Maps API key 就會顯示地圖。key 只存在這支手機的瀏覽器裡，不會進到程式碼。')+'</p>'+
    '<input type="text" inputmode="latin" autocomplete="off" spellcheck="false" placeholder="AIza…" aria-label="Google Maps API key">'+
    '<button type="submit">儲存並載入</button></form>';
  el.querySelector('form').addEventListener('submit',e=>{
    e.preventDefault();
    const v=el.querySelector('input').value.trim();if(!v)return;
    try{localStorage.setItem(GKEY,v);}catch(err){}
    gmLib=null;
    document.querySelectorAll('.gmap').forEach(x=>{x.classList.remove('nokey');x.textContent='';if(x._init)x._init();});
  });
}
function clearKey(){try{localStorage.removeItem(GKEY);}catch(e){}location.reload();}
const pinClass=p=>'pin'+(p.brand?' p-'+p.brand:'')+(p.state?' '+p.state:'');
function pinEl(p){
  const d=document.createElement('div');
  d.className=pinClass(p);d.textContent=p.no;d.title=p.label;
  return d;
}
const pinZ=s=>s==='next'?9:s==='done'?1:5;
// el：.gmap 容器；pts：[{ll:"lat,lng", no, label, brand?, state?, url?}]
function mountMap(el,pts){
  // 覆蓋層（資訊卡、控制鈕）要相對於地圖本身定位，把 .gmap 包進 .map-inner
  if(!el.parentNode.classList.contains('map-inner')){
    const inner=document.createElement('div');inner.className='map-inner';
    el.parentNode.insertBefore(inner,el);inner.appendChild(el);
  }
  const init=()=>{
    const lib=loadGmaps();
    if(!lib){keyForm(el);return;}
    el.classList.remove('nokey');el.textContent='';
    lib.then(({Map,Marker})=>{
      // 全螢幕改由我們做：.map-inner 加 .fs 用 position:fixed 鋪滿視窗（不用 Fullscreen API），
      // 切去 Google Maps app 再回來狀態不會掉；UI 元件用 safe-area 當內距往內縮
      const map=new Map(el,{mapId:'DEMO_MAP_ID',gestureHandling:'greedy',mapTypeControl:false,streetViewControl:false,zoomControl:false,cameraControl:false,rotateControl:false,clickableIcons:false,fullscreenControl:false});
      map.controls[google.maps.ControlPosition.RIGHT_TOP].push(fsButton(el.parentNode));
      const b=new google.maps.LatLngBounds();
      // 覆蓋層全部走 map.controls 放進地圖內部，全螢幕時才看得到
      const card=mapCard(el);
      map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(card.box);
      const markers=pts.map(p=>{
        const [lat,lng]=p.ll.split(',').map(Number);b.extend({lat,lng});
        const m=new Marker({map,position:{lat,lng},content:pinEl(p),title:p.label,zIndex:pinZ(p.state),gmpClickable:true});
        let last=0;const tap=()=>{const t=Date.now();if(t-last<300)return;last=t;card.show(p,m);map.panTo({lat,lng});if(p.onTap)p.onTap();};
        m.addEventListener('gmp-click',tap);
        m.content.addEventListener('click',e=>{e.stopPropagation();tap();});
        return m;
      });
      map.addListener('click',()=>card.hide());
      map.fitBounds(b,36);
      el._map={map,markers,pts,card,Marker};
      allMaps.push(el);
      mapControls(el);
      if(el._onReady)el._onReady(el._map);
    }).catch(err=>{el.innerHTML='<p class="map-err">'+err.message+'</p>';});
  };
  el._init=init;init();
}
// 地圖底部資訊卡：點圖釘顯示，點地圖空白處或 × 關閉
const fmtDist=d=>d<950?Math.round(d/10)*10+' m':(d/1000).toFixed(1)+' km';
function mapCard(el){
  const box=document.createElement('div');box.className='map-card';box.hidden=true;
  // 外層用內距（不是邊距）推開導覽列：Google 的控制容器量高度時不含子元素的邊距
  const outer=document.createElement('div');outer.className='map-card-wrap';outer.appendChild(box);
  let cur=null,curM=null;
  const placeUrl=p=>p.url||('https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(p.label));
  const navUrl=p=>'https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(p.ll)+'&travelmode=walking&dir_action=navigate';
  const api={selId:null,box:outer};
  api.refresh=()=>{
    if(!cur)return;
    const p=cur,isDone=p.id&&done.has(p.id);
    // 餐廳圖釘（p.img／p.score／p.url2）：縮圖取代編號、副標顯示分數、多一顆 Google 地圖鈕
    box.innerHTML='<div class="mc-head">'+
      (p.img?'<img class="mc-photo" src="'+p.img+'" alt="" onerror="this.style.visibility=\'hidden\'">':
       p.dex?'<img class="mc-spr" src="'+SPRITE(p.dex)+'" alt="" onerror="this.style.visibility=\'hidden\'">':'<span class="mc-no">'+p.no+'</span>')+
      '<div class="mc-txt"><div class="mc-name">'+(p.img?'<span class="mc-rank">'+p.no+'</span>':'')+p.label+'</div>'+
      '<div class="mc-sub">'+(p.time||'')+(p.score?'<span class="mc-score">食べログ '+p.score+'</span>':'')+
      (p.brand&&!p.score?'<span class="pill p-'+p.brand+'">'+p.brand+'</span>':'')+
      (mePos?'<span class="mc-dist">距你 '+fmtDist(distM(mePos,llOf(p)))+'</span>':'')+'</div>'+
      '</div><button type="button" class="mc-x" aria-label="關閉">×</button></div>'+
      (p.note?'<div class="mc-note">'+p.note+'</div>':'')+
      '<div class="mc-acts">'+
      '<a class="mapbtn rt" href="'+placeUrl(p)+'" target="_blank" rel="noopener">'+icon('town-map','🗺')+(p.urlLabel||'打開地點')+'</a>'+
      (p.url2?'<a class="mapbtn rt" href="'+p.url2+'" target="_blank" rel="noopener">'+icon('town-map','🗺')+'Google 地圖</a>':'')+
      '<a class="mapbtn rt" href="'+navUrl(p)+'" target="_blank" rel="noopener">'+icon('dowsing-machine','🧭')+'導航</a>'+
      (p.id?'<button type="button" class="mapbtn rt mt mc-done'+(isDone?' on':'')+'">'+icon('poke-ball','●')+(isDone?'取消完成':'完成')+'</button>':'')+
      '</div>';
    box.querySelector('.mc-x').addEventListener('click',api.hide);
    const dn=box.querySelector('.mc-done');
    if(dn)dn.addEventListener('click',()=>{const li=document.querySelector('.stop[data-id="'+p.id+'"]');if(li)li.click();api.refresh();});
  };
  api.show=(p,m)=>{
    if(curM)curM.content.classList.remove('sel');
    cur=p;curM=m;api.selId=p.id||null;m.content.classList.add('sel');
    api.refresh();box.style.width=Math.min(el.clientWidth-16,520)+'px';box.hidden=false;
  };
  api.hide=()=>{if(curM)curM.content.classList.remove('sel');cur=null;curM=null;api.selId=null;box.hidden=true;};
  return api;
}
// 自製全螢幕：.map-inner 加 .fs（position:fixed 鋪滿視窗），不用 Fullscreen API——
// 真全螢幕在切到 Google Maps app 時會被瀏覽器自動退出，回來後沒有點擊事件不准再進去；CSS 狀態則會留著。
// 進入時 pushState 一筆，讓 Android 返回鍵／手勢是「退出全螢幕」而不是離開頁面。
function setFs(inner,on){
  inner.classList.toggle('fs',on);document.body.classList.toggle('fs-lock',on);
  const b=inner.querySelector('.fs-btn');if(b){b.textContent=on?'✕ 退出':'⛶ 全螢幕';b.classList.toggle('on',on);}
  const gm=inner.querySelector('.gmap');if(gm&&gm._map&&window.google)google.maps.event.trigger(gm._map.map,'resize');
}
function exitFs(){
  const cur=document.querySelector('.map-inner.fs');if(!cur)return false;
  setFs(cur,false);return true;
}
function fsButton(inner){
  const b=document.createElement('button');b.type='button';b.className='mctl fs-btn';b.textContent='⛶ 全螢幕';
  b.addEventListener('click',()=>{
    if(inner.classList.contains('fs')){
      if(history.state&&history.state.fs)history.back();else exitFs();
    }else{
      exitFs();history.pushState({fs:1},'');setFs(inner,true);
    }
  });
  return b;
}
// 返回鍵：先退全螢幕，沒有全螢幕才關餐廳 dialog（兩者各 pushState 一筆，順序剛好相反）
window.addEventListener('popstate',()=>{if(!exitFs())closeDlg();});
document.addEventListener('keydown',e=>{
  if(e.key!=='Escape')return;
  if(document.querySelector('.map-inner.fs')){if(history.state&&history.state.fs)history.back();else exitFs();return;}
  requestCloseDlg();
});
function pinState(id){
  if(done.has(id))return 'done';
  const nxt=ALL.find(x=>!done.has(x[1]));
  return nxt&&nxt[1]===id?'next':'';
}
// 路跑 37 站 → 圖釘資料。half：'am'（飯店＋P1＋P2）或 'pm'（P3）
function runPts(half){
  const cut=P1.length+P2.length;
  const pts=ALL.map(([d,id],i)=>{
    const c=COORDS[d[4]];
    if(!c||(half==='pm')!==(i>=cut))return null;
    return {ll:c,no:String(i+1).padStart(2,'0'),label:d[1],time:d[0],note:d[3],dex:i+1,brand:d[2],id,half,state:pinState(id),
      url:d[4].indexOf('http')===0?d[4]:'https://maps.google.com/?cid='+d[4]};
  }).filter(Boolean);
  if(half==='am')pts.unshift({ll:HOTEL[1],no:'H',label:HOTEL[0],half,state:'hotel'});
  return pts;
}
function refreshRunPins(){
  runMaps.forEach(el=>{
    const M=el._map;if(!M)return;
    let changed=false;
    M.markers.forEach((m,i)=>{
      const p=M.pts[i];if(!p.id)return;
      const s=pinState(p.id);if(s===p.state)return;
      p.state=s;changed=true;m.content.className=pinClass(p)+(M.card.selId===p.id?' sel':'');m.zIndex=pinZ(s);
      if(M.card.selId===p.id)M.card.refresh();
    });
    if(changed&&isRunDay()&&el===runMaps[0])focusNext(el);
  });
}
// wrap：容器，裡面放上午／下午切換與 .gmap。所有圖釘一次建好，切換只是顯示／隱藏＋重新取景
function buildRunMap(wrap){
  wrap.innerHTML='<div class="chips"><button type="button" class="chip on" data-half="am">上午 '+(P1.length+P2.length)+' 站</button>'+
    '<button type="button" class="chip" data-half="pm">下午 '+P3.length+' 站</button></div><div class="gmap"></div>';
  const el=wrap.querySelector('.gmap');runMaps.push(el);
  const chips=wrap.querySelector('.chips');chips.hidden=true;
  let half='am';
  const apply=()=>{
    const M=el._map;if(!M)return;
    const b=new google.maps.LatLngBounds();
    M.markers.forEach((m,i)=>{const on=M.pts[i].half===half;m.map=on?M.map:null;if(on)b.extend(m.position);});
    M.map.fitBounds(b,36);
  };
  const setHalf=h=>{if(h===half)return;half=h;wrap.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x.dataset.half===h));apply();};
  el._setHalf=setHalf;
  el._onReady=()=>{
    el._map.map.controls[google.maps.ControlPosition.TOP_CENTER].push(chips);chips.hidden=false;
    apply();if(isRunDay()){startGeo(()=>focusNext(el));focusNext(el);}
  };
  wrap.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>setHalf(c.dataset.half)));
  mountMap(el,runPts('am').concat(runPts('pm')));
}
// 9/16 以外的日子：ROUTES 的點依序編 1、2、3…，同一地點出現兩次只標一次
function dayPts(date){
  const pts=[],seen={};
  (ROUTES[date]||[]).forEach(p=>{if(seen[p[1]])return;seen[p[1]]=1;pts.push({ll:p[1],no:String(pts.length+1),label:p[0]});});
  return pts;
}
// 行程日卡：標題列右側的「地圖」按鈕展開地圖，第一次展開才建立（省載入次數）
function dayMapToggle(card,date,head,before){
  const pts=date==='9/16'?null:dayPts(date);
  if(pts&&!pts.length)return;
  const btn=document.createElement('button');btn.type='button';btn.className='mapbtn rt mt';btn.innerHTML=icon('poke-radar','📍')+'地圖';
  (head.querySelector('.day-btns')||head).appendChild(btn);
  const wrap=document.createElement('div');wrap.className='day-map map-box';wrap.hidden=true;card.insertBefore(wrap,before);
  btn.addEventListener('click',e=>{
    e.stopPropagation();
    wrap.hidden=!wrap.hidden;btn.classList.toggle('on',!wrap.hidden);
    if(wrap.hidden||wrap.dataset.ready)return;
    wrap.dataset.ready='1';
    if(pts){wrap.innerHTML='<div class="gmap"></div>';mountMap(wrap.firstChild,pts);}
    else buildRunMap(wrap);
  });
}

// 行程日卡：「午餐」「晚餐」兩顆鈕，各開一個全螢幕 dialog：地圖固定在最上面、下面是名單（MEALS，由 notes/gen_meals.py 產生）
// 名單依距離排序（預設車站距離；按「距我」改成離目前位置），類型 chip 可多選篩選；圖釘編號＝目前名單順序
// 名單捲動時地圖自動移到目前最上面那家（圖釘與該列一起標記）；點圖釘則把名單捲到那家。dialog 第一次開才建
const MEAL_IMG='https://tblg.k-img.com/restaurant/images/Rvw/';
const gmapUrl=n=>'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(n);
const dlgs=[];   // 已建立的 dialog（同時只會開一個）
function openDlg(d){
  closeDlg();
  d.el.hidden=false;d.open=true;document.body.classList.add('dlg-lock');
  history.pushState({mdlg:1},'');
  // 地圖要在容器看得見之後才建（display:none 時建出來尺寸是 0，取景會壞）
  if(!d.ready){d.ready=true;d.mount();}
  else{const gm=d.el.querySelector('.gmap');if(gm&&gm._map&&window.google)google.maps.event.trigger(gm._map.map,'resize');}
}
function closeDlg(){
  const d=dlgs.find(x=>x.open);if(!d)return false;
  d.el.hidden=true;d.open=false;document.body.classList.remove('dlg-lock');return true;
}
// 關閉鈕／Esc：有 pushState 過就走 history.back()（popstate 會關），沒有就直接關
function requestCloseDlg(){
  if(!dlgs.some(x=>x.open))return false;
  if(history.state&&history.state.mdlg)history.back();else closeDlg();
  return true;
}
function dayMealToggle(card,date,head){
  const m=typeof MEALS!=='undefined'&&MEALS[date];
  if(!m)return;
  [['lunch','午餐','lava-cookie','🍱'],['dinner','晚餐','moomoo-milk','🍶']].forEach(([k,label,ic,fb])=>{
    const s=m[k];if(!s||!s.list.length)return;
    const btn=document.createElement('button');btn.type='button';btn.className='mapbtn rt mt meal '+k;btn.innerHTML=icon(ic,fb)+label;
    (head.querySelector('.day-btns')||head).appendChild(btn);
    let d=null;
    btn.addEventListener('click',e=>{e.stopPropagation();if(!d){d=mealDlg(date+' '+label,s,k);dlgs.push(d);}openDlg(d);});
  });
}
// 距離字串「秋葉原駅 432m」→ 432；沒數字的（中禅寺温泉／日光市街）排最後、彼此維持原本的評分順序
const stMeters=t=>{const x=/(\d+)\s*m\b/.exec(t);return x?+x[1]:Infinity;};
function mealDlg(title,s,k){
  // 每列：[店名, 類型, 分數, 距離, 預算, Tabelog 連結, "lat,lng", [縮圖…]]
  const cnt={};
  s.list.forEach(o=>o[1].split('・').forEach(t=>{cnt[t]=(cnt[t]||0)+1;}));
  const types=Object.keys(cnt).sort((a,b)=>cnt[b]-cnt[a]||a.localeCompare(b,'zh-Hant'));
  const el=document.createElement('div');el.className='mdlg';el.hidden=true;
  el.innerHTML='<div class="mdlg-head"><div class="mdlg-tt"><div class="mdlg-title">'+title+'</div><div class="mdlg-note">'+s.note+'</div></div>'+
    '<button type="button" class="mdlg-x" aria-label="關閉">×</button></div>'+
    '<div class="map-box"><div class="gmap"></div></div>'+
    '<div class="mdlg-tools"><div class="mdlg-chips"><button type="button" class="chip on" data-t="">全部</button>'+
    types.map(t=>'<button type="button" class="chip" data-t="'+t+'">'+t+'<b>'+cnt[t]+'</b></button>').join('')+'</div>'+
    '<div class="mdlg-sort"><button type="button" class="chip on" data-s="st">近 → 遠（車站）</button><button type="button" class="chip" data-s="me">◎ 距我</button><span class="mdlg-n"></span></div></div>'+
    '<ul class="mdlg-list meal-list"></ul>';
  document.body.appendChild(el);
  const gm=el.querySelector('.gmap'),ul=el.querySelector('.mdlg-list'),nEl=el.querySelector('.mdlg-n');
  const sel=new Set();let sortMode='st',vis=[],cur=null;
  const d={el,open:false,ready:false};
  // 每列的 li 只建一次，之後篩選／排序只是重排與顯示／隱藏
  const rows=s.list.map((o,i)=>{
    const li=document.createElement('li');li.className='opt meal-opt';li.tabIndex=0;li.hidden=true;
    li.innerHTML='<div class="opt-line"><span class="opt-no p-'+k+'"></span><span class="opt-name">'+o[0]+'</span>'+
      '<span class="opt-score">食べログ '+o[2]+'</span><span class="opt-tag">'+o[1]+'</span></div>'+
      '<div class="opt-note">'+o[3]+' · '+o[4]+'<span class="opt-me"></span></div>'+
      (o[7]&&o[7].length?'<div class="meal-pics">'+o[7].map(u=>'<img src="'+MEAL_IMG+u+'" alt="" loading="lazy" onerror="this.remove()">').join('')+'</div>':'')+
      '<div class="stop-foot"><a class="mapbtn" href="'+o[5]+'" target="_blank" rel="noopener">食べログ ↗</a>'+
      '<a class="mapbtn" href="'+gmapUrl(o[0])+'" target="_blank" rel="noopener">Google 地圖 ↗</a></div>';
    li.querySelectorAll('a').forEach(a=>a.addEventListener('click',e=>e.stopPropagation()));
    const r={o,i,li,ll:o[6]?llOf({ll:o[6]}):null,st:stMeters(o[3]),types:o[1].split('・'),p:null,m:null};
    const go=()=>{const M=gm._map;if(!M||!r.m)return;setCur(r,false);panCard(M,r,true);};
    li.addEventListener('click',go);
    li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});
    ul.appendChild(li);
    return r;
  });
  const pts=[];
  rows.forEach(r=>{
    if(!r.ll)return;
    const o=r.o;
    r.p={ll:o[6],no:String(r.i+1),ri:r.i,label:o[0],brand:k,score:o[2],note:o[1]+' · '+o[3]+' · '+o[4],
      url:o[5],urlLabel:'食べログ',url2:gmapUrl(o[0]),img:o[7]&&o[7][0]?MEAL_IMG+o[7][0]:'',
      // 點圖釘：名單捲到這家（捲動跟隨會接著把它設成目前列）
      onTap:()=>{setCur(r,false);ul.scrollTop=r.li.offsetTop;}};
    pts.push(r.p);
  });
  const panTo=(M,r)=>{M.map.panTo(r.ll);if(M.map.getZoom()<16)M.map.setZoom(16);};
  const panCard=(M,r,openCard)=>{panTo(M,r);if(openCard)M.card.show(r.p,r.m);};
  // 目前列：名單列與圖釘一起標記；pan=true 時地圖移過去並收起資訊卡
  function setCur(r,pan){
    if(cur===r)return;
    if(cur){cur.li.classList.remove('cur');if(cur.m){cur.m.content.classList.remove('cur');cur.m.zIndex=pinZ('');}}
    cur=r;if(!r)return;
    r.li.classList.add('cur');
    if(r.m){r.m.content.classList.add('cur');r.m.zIndex=9;}
    const M=gm._map;
    if(pan&&M&&r.m){M.card.hide();panTo(M,r);}
  }
  function fitVis(){
    const M=gm._map;if(!M)return;
    const on=vis.filter(r=>r.m);if(!on.length)return;
    M.card.hide();
    if(on.length===1){panTo(M,on[0]);return;}
    const b=new google.maps.LatLngBounds();on.forEach(r=>b.extend(r.ll));M.map.fitBounds(b,36);
  }
  function render(fit){
    const list=rows.filter(r=>!sel.size||r.types.some(t=>sel.has(t)));
    const key=sortMode==='me'&&mePos?r=>r.ll?distM(mePos,r.ll):Infinity:r=>r.st;
    list.sort((a,b)=>key(a)-key(b)||a.i-b.i);
    const M=gm._map;
    rows.forEach(r=>{r.li.hidden=true;if(r.m)r.m.map=null;});
    list.forEach((r,n)=>{
      ul.appendChild(r.li);r.li.hidden=false;
      r.li.querySelector('.opt-no').textContent=n+1;
      r.li.querySelector('.opt-me').textContent=(sortMode==='me'&&mePos&&r.ll)?' · 距你 '+fmtDist(distM(mePos,r.ll)):'';
      if(r.p)r.p.no=String(n+1);
      if(r.m){r.m.map=M.map;r.m.content.textContent=n+1;}
    });
    vis=list;
    nEl.textContent=list.length+' 家';
    ul.scrollTop=0;setCur(list[0]||null,false);
    if(fit)fitVis();
  }
  // 捲動跟隨：找目前露出超過一半（或 56px）的第一列
  let raf=0;
  ul.addEventListener('scroll',()=>{
    if(raf)return;
    raf=requestAnimationFrame(()=>{
      raf=0;const top=ul.scrollTop;
      const r=vis.find(x=>x.li.offsetTop+x.li.offsetHeight-top>Math.min(x.li.offsetHeight*.5,56));
      if(r&&r!==cur)setCur(r,true);
    });
  },{passive:true});
  el.querySelectorAll('.mdlg-chips .chip').forEach(c=>c.addEventListener('click',()=>{
    const t=c.dataset.t;
    if(!t)sel.clear();else if(sel.has(t))sel.delete(t);else sel.add(t);
    el.querySelectorAll('.mdlg-chips .chip').forEach(x=>x.classList.toggle('on',x.dataset.t?sel.has(x.dataset.t):!sel.size));
    render(true);
  }));
  const setSort=mode=>{sortMode=mode;el.querySelectorAll('.mdlg-sort .chip').forEach(x=>x.classList.toggle('on',x.dataset.s===mode));render(true);};
  el.querySelectorAll('.mdlg-sort .chip').forEach(c=>c.addEventListener('click',()=>{
    if(c.dataset.s==='me')startGeo(()=>setSort('me'));else setSort('st');
  }));
  el.querySelector('.mdlg-x').addEventListener('click',requestCloseDlg);
  d.mount=()=>{
    render(false);
    if(!pts.length){gm.parentNode.remove();return;}
    gm._onReady=M=>{
      pts.forEach((p,j)=>{rows[p.ri].m=M.markers[j];});
      render(true);
    };
    mountMap(gm,pts);
  };
  return d;
}

function render(){
  const r1=document.getElementById('rail1'),r2=document.getElementById('rail2'),r3=document.getElementById('rail3');
  r1.innerHTML='';r2.innerHTML='';r3.innerHTML='';
  P1.forEach((d,i)=>r1.appendChild(stopEl(d,'a'+i,i+1)));
  P2.forEach((d,i)=>r2.appendChild(stopEl(d,'b'+i,P1.length+i+1)));
  P3.forEach((d,i)=>r3.appendChild(stopEl(d,'c'+i,P1.length+P2.length+i+1)));
  buildRunMap(document.getElementById('runmap-wrap'));
  document.getElementById('mapkey').addEventListener('click',()=>{
    if(confirm('清除這支手機上存的 Google Maps key？'))clearKey();
  });

  const ph=document.getElementById('phrases');
  PHRASES.forEach(p=>{
    const el=document.createElement('div');
    el.className='ph';el.tabIndex=0;
    el.innerHTML='<div class="ph-when">'+p[0]+'</div><div class="ph-jp">'+p[1]+'</div><div class="ph-tc">'+p[2]+'</div>';
    const t=()=>el.classList.toggle('big');
    el.addEventListener('click',t);
    el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();t();}});
    ph.appendChild(el);
  });

  const pp=document.getElementById('prep');
  PREP.forEach((p,i)=>{
    const li=document.createElement('li');li.tabIndex=0;
    if(prepDone.has(i))li.classList.add('on');
    li.innerHTML='<span class="prep-cat">'+p[0]+'</span><span>'+p[1]+'</span>';
    const g=()=>{
      if(prepDone.has(i)){prepDone.delete(i);}else{prepDone.add(i);}
      li.classList.toggle('on');savePrep();
    };
    li.addEventListener('click',g);
    li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();g();}});
    pp.appendChild(li);
  });

  const rc=document.getElementById('recon');
  RECON.forEach(t=>{
    const li=document.createElement('li');li.tabIndex=0;
    li.innerHTML='<span>'+t+'</span>';
    const g=()=>li.classList.toggle('on');
    li.addEventListener('click',g);
    li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();g();}});
    rc.appendChild(li);
  });

  const dv=document.getElementById('days');
  DAYS.forEach(d=>{
    const el=document.createElement('div');
    el.className='day tl'+(d[4]?' hot':'');
    el.innerHTML='<div class="day-head"><span class="day-d">'+d[0]+' '+d[1]+'</span><span class="day-t">'+d[2]+'</span><span class="day-btns"></span></div><ul class="day-tl"></ul>';
    const ul=el.querySelector('.day-tl');
    dayMapToggle(el,d[0],el.querySelector('.day-head'),ul);
    dayMealToggle(el,d[0],el.querySelector('.day-head'),ul);
    d[3].forEach(it=>{
      const li=document.createElement('li');
      if(it[2])li.className='key';
      const opts=it[3];
      if(!opts||!opts.length){
        li.innerHTML='<span class="tl-t">'+it[0]+'</span><span>'+it[1]+'</span>';
      }else{
        li.classList.add('pick');li.tabIndex=0;
        li.innerHTML='<span class="tl-t">'+it[0]+'</span>'+
          '<div class="tl-body"><div class="tl-line"><span>'+it[1]+'</span>'+
          '<span class="tl-badge">'+opts.length+' 選<span class="tl-caret">▾</span></span></div>'+
          '<ul class="tl-opts">'+opts.map(o=>
            '<li class="opt"><div class="opt-line"><span class="opt-name">'+o[0]+'</span>'+
            '<span class="opt-tag">'+o[1]+'</span><span class="opt-score">食べログ '+o[2]+'</span></div>'+
            '<div class="opt-note">'+o[3]+'</div>'+
            '<div class="stop-foot"><a class="mapbtn" href="'+o[4]+'" target="_blank" rel="noopener">開地圖 ↗</a></div></li>'
          ).join('')+'</ul></div>';
        li.querySelectorAll('.mapbtn').forEach(a=>a.addEventListener('click',e=>e.stopPropagation()));
        const t=()=>li.classList.toggle('open');
        li.addEventListener('click',t);
        li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();t();}});
      }
      ul.appendChild(li);
    });
    dv.appendChild(el);
  });

  const bk=document.getElementById('bookings');
  BOOKINGS.forEach(b=>{
    const el=document.createElement('div');
    el.className='day';
    el.innerHTML='<div class="day-d">'+b[0]+'</div><div><div class="day-t"><span class="bk-tag">'+b[1]+'</span>'+b[2]+'</div><div class="day-b">'+b[3]+'</div>'+
      (b[4]?'<div class="stop-foot"><a class="mapbtn" href="'+(b[4].indexOf('http')===0?b[4]:'https://maps.google.com/?cid='+b[4])+'" target="_blank" rel="noopener">開地圖 ↗</a></div>':'')+'</div>';
    bk.appendChild(el);
  });
  updateBar();
}

function updateBar(){
  document.getElementById('count').textContent=done.size+'/'+ALL.length;
  const idx=ALL.findIndex(x=>!done.has(x[1]));
  const spr=document.getElementById('barSprite');
  if(idx>-1){
    document.getElementById('nextLabel').textContent='下一站 · '+ALL[idx][0][0];
    document.getElementById('nextName').textContent=ALL[idx][0][1];
    spr.src=SPRITE(idx+1);spr.hidden=false;
  }else{
    document.getElementById('nextLabel').textContent='全部收工';
    document.getElementById('nextName').textContent='回秋葉原開包 🎉';
    spr.src=SPRITE(25);spr.hidden=false;
  }
  refreshRunPins();
}

document.getElementById('reset').addEventListener('click',()=>{
  done.clear();saveDone();
  document.querySelectorAll('.stop.done').forEach(e=>e.classList.remove('done'));
  updateBar();
});

// 分頁切換：記住上次停留的分頁，下次開啟直接回到該頁
const VIEW_KEY='tokyo2026:view';
function showView(name){
  if(!document.getElementById('v-'+name))name='run';
  document.querySelectorAll('.nav button').forEach(x=>x.classList.toggle('on',x.dataset.v===name));
  document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v.id==='v-'+name));
  try{localStorage.setItem(VIEW_KEY,name);}catch(e){}
}
document.querySelectorAll('.nav button').forEach(b=>{
  b.addEventListener('click',()=>{showView(b.dataset.v);window.scrollTo(0,0);});
});
try{const v=localStorage.getItem(VIEW_KEY);if(v&&v!=='run')showView(v);}catch(e){}

const TARGET=new Date('2026-09-16T07:00:00+09:00').getTime();
function tick(){
  const now=new Date();
  const jst=new Date(now.toLocaleString('en-US',{timeZone:'Asia/Tokyo'}));
  document.getElementById('clock').textContent=
    String(jst.getHours()).padStart(2,'0')+':'+String(jst.getMinutes()).padStart(2,'0');
  let diff=TARGET-now.getTime();
  if(diff<0){diff=-diff;document.getElementById('cdTag').textContent='已開賣';}
  document.getElementById('cdD').textContent=String(Math.floor(diff/864e5)).padStart(2,'0');
  document.getElementById('cdH').textContent=String(Math.floor(diff/36e5)%24).padStart(2,'0');
  document.getElementById('cdM').textContent=String(Math.floor(diff/6e4)%60).padStart(2,'0');
}
tick();setInterval(tick,1000);

loadDone();
loadPrep();
render();
loadDex();

if('serviceWorker' in navigator){
  navigator.serviceWorker.register('sw.js').catch(()=>{/* 註冊失敗不影響使用 */});
}
