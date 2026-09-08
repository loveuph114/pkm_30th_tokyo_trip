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
  li.tabIndex=0;
  li.innerHTML=
    '<div class="stop-time">'+time+'</div>'+
    '<div class="dex">'+
      '<img src="'+SPRITE(no)+'" alt="" loading="lazy" onerror="this.style.visibility=\'hidden\'">'+
      '<span class="dex-no">'+String(no).padStart(3,'0')+'</span></div>'+
    '<div><div class="stop-name">'+name+'</div>'+
    '<div class="stop-note">'+note+'</div>'+
    '<div class="stop-foot"><span class="pill p-'+brand+'">'+brand+'</span>'+
    '<a class="mapbtn" href="'+(cid.indexOf('http')===0?cid:'https://maps.google.com/?cid='+cid)+'" target="_blank" rel="noopener">開地圖 \u2197</a>'+
    '<span class="dex-name" data-no="'+no+'"></span></div></div>';
  li.querySelector('.mapbtn').addEventListener('click',e=>e.stopPropagation());
  const toggle=function(){
    if(done.has(id)){done.delete(id);}else{done.add(id);}
    li.classList.toggle('done');saveDone();updateBar();
  };
  li.addEventListener('click',toggle);
  li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}});
  return li;
}

// ── 整日路線：Google Maps 多點路線連結 ──
// 一段最多 SEG_MAX 點（App 上限 9 個中途點＋起終點）。超過就切段，段與段首尾共用一點，路線不斷
const SEG_MAX=10;
function dirUrl(pts,mode){
  const enc=p=>encodeURIComponent(p[1]);
  let u='https://www.google.com/maps/dir/?api=1&origin='+enc(pts[0])+'&destination='+enc(pts[pts.length-1]);
  if(pts.length>2)u+='&waypoints='+pts.slice(1,-1).map(enc).join('%7C');
  return u+'&travelmode='+mode;
}
function chunk(pts){
  const n=pts.length;if(n<=SEG_MAX)return [pts];
  const k=Math.ceil((n-1)/(SEG_MAX-1)),out=[];
  for(let i=0;i<k;i++){const a=Math.round(i*(n-1)/k),b=Math.round((i+1)*(n-1)/k);out.push(pts.slice(a,b+1));}
  return out;
}
// 站點 → 路線點 [名稱, 座標, 圖鑑編號]；沒座標的站略過（console 警告，不擋畫面）
function stopPts(list,offset){
  return list.map((d,i)=>{
    const c=COORDS[d[4]];
    if(!c)console.warn('COORDS 缺少座標：',d[1]);
    return c?[d[1],c,offset+i+1]:null;
  }).filter(Boolean);
}
const NO=n=>String(n).padStart(2,'0');
function segLabel(prefix,idx,pts){
  const a=pts[0][2],b=pts[pts.length-1][2];
  return prefix+' '+'①②③④⑤⑥⑦⑧⑨'[idx]+' '+(a?NO(a):'飯店')+'→'+NO(b);
}
// 9/16 分上下半天：上午＝飯店→P1、P2（各自切段）；下午＝P3 錦糸町、P3 秋葉原
function runSegments(){
  const p1=[[HOTEL[0],HOTEL[1],0]].concat(stopPts(P1,0));
  const p2=stopPts(P2,P1.length);
  const p3=stopPts(P3,P1.length+P2.length);
  const c1=chunk(p1),c2=chunk(p2);
  const am=c1.concat(c2).map((pts,i)=>({label:segLabel('上午',i,pts),mode:'walking',pts}));
  const pm=[p3.slice(0,P3_SPLIT),p3.slice(P3_SPLIT)].filter(x=>x.length>1)
    .map((pts,i)=>({label:'下午 '+'①②'[i]+' '+(i===0?'錦糸町':'秋葉原'),mode:'walking',pts}));
  return {am,pm,p1:am.slice(0,c1.length)};
}
function daySegments(date){
  if(date==='9/16'){const r=runSegments();return r.am.concat(r.pm);}
  const out=[];
  (ROUTES[date]||[]).forEach(seg=>{
    if(seg[2]==='P1'){runSegments().p1.forEach((s,i)=>out.push({label:seg[0]+' '+'①②③'[i],mode:seg[1],pts:s.pts,quiet:true}));return;}
    chunk(seg[2]).forEach((pts,i,arr)=>out.push({label:seg[0]+(arr.length>1?' '+'①②③④'[i]:''),mode:seg[1],pts,names:true}));
  });
  return out;
}
function routesEl(segs){
  const div=document.createElement('div');div.className='routes';
  if(!segs.length)return div;
  div.innerHTML=segs.map(s=>'<a class="mapbtn rt" href="'+dirUrl(s.pts,s.mode)+'" target="_blank" rel="noopener">🗺 '+s.label+'</a>').join('');
  const named=segs.filter(s=>s.names);
  if(named.length){
    const p=document.createElement('div');p.className='rt-pts';
    p.textContent=named.map(s=>s.pts.map(x=>x[0]).join(' → ')).join('　／　');
    div.appendChild(p);
  }
  div.querySelectorAll('a').forEach(a=>a.addEventListener('click',e=>e.stopPropagation()));
  return div;
}

// ── Google Maps（key 由使用者在 app 裡貼一次，存 localStorage，不進 repo）──
// 圖釘用 AdvancedMarkerElement + DEMO_MAP_ID（Google 提供的預設樣式 map id，不用另建）
const GKEY='tokyo2026:gmapkey';
let gmLib=null;      // Promise → {Map,Marker}
const runMaps=[];    // 路跑地圖的 .gmap 元素，勾選站點時同步更新圖釘
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
  const init=()=>{
    const lib=loadGmaps();
    if(!lib){keyForm(el);return;}
    el.classList.remove('nokey');el.textContent='';
    lib.then(({Map,Marker})=>{
      const map=new Map(el,{mapId:'DEMO_MAP_ID',gestureHandling:'greedy',mapTypeControl:false,streetViewControl:false,clickableIcons:false});
      const b=new google.maps.LatLngBounds();
      const markers=pts.map(p=>{
        const [lat,lng]=p.ll.split(',').map(Number);b.extend({lat,lng});
        const m=new Marker({map,position:{lat,lng},content:pinEl(p),title:p.label,zIndex:pinZ(p.state)});
        m.addEventListener('gmp-click',()=>window.open(p.url||('https://www.google.com/maps/search/?api=1&query='+lat+'%2C'+lng),'_blank','noopener'));
        return m;
      });
      map.fitBounds(b,36);
      el._map={map,markers,pts};
      if(el._onReady)el._onReady(el._map);
    }).catch(err=>{el.innerHTML='<p class="map-err">'+err.message+'</p>';});
  };
  el._init=init;init();
}
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
    return {ll:c,no:String(i+1).padStart(2,'0'),label:d[0]+' '+d[1],brand:d[2],id,half,state:pinState(id),
      url:d[4].indexOf('http')===0?d[4]:'https://maps.google.com/?cid='+d[4]};
  }).filter(Boolean);
  if(half==='am')pts.unshift({ll:HOTEL[1],no:'H',label:HOTEL[0],half,state:'hotel'});
  return pts;
}
function refreshRunPins(){
  runMaps.forEach(el=>{
    const M=el._map;if(!M)return;
    M.markers.forEach((m,i)=>{
      const p=M.pts[i];if(!p.id)return;
      const s=pinState(p.id);if(s===p.state)return;
      p.state=s;m.content.className=pinClass(p);m.zIndex=pinZ(s);
    });
  });
}
// wrap：容器，裡面放上午／下午切換與 .gmap。所有圖釘一次建好，切換只是顯示／隱藏＋重新取景
function buildRunMap(wrap){
  wrap.innerHTML='<div class="chips"><button type="button" class="chip on" data-half="am">上午 '+(P1.length+P2.length)+' 站</button>'+
    '<button type="button" class="chip" data-half="pm">下午 '+P3.length+' 站</button></div><div class="gmap"></div>';
  const el=wrap.querySelector('.gmap');runMaps.push(el);
  let half='am';
  const apply=()=>{
    const M=el._map;if(!M)return;
    const b=new google.maps.LatLngBounds();
    M.markers.forEach((m,i)=>{const on=M.pts[i].half===half;m.map=on?M.map:null;if(on)b.extend(m.position);});
    M.map.fitBounds(b,36);
  };
  el._onReady=apply;
  wrap.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>{
    half=c.dataset.half;
    wrap.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===c));
    apply();
  }));
  mountMap(el,runPts('am').concat(runPts('pm')));
}
// 9/16 以外的日子：ROUTES 的點依序編 1、2、3…，同一地點出現兩次只標一次
function dayPts(date){
  const pts=[],seen={};
  (ROUTES[date]||[]).forEach(seg=>{
    if(seg[2]==='P1')return;
    seg[2].forEach(p=>{if(seen[p[1]])return;seen[p[1]]=1;pts.push({ll:p[1],no:String(pts.length+1),label:p[0]});});
  });
  return pts;
}
// 行程日卡：「📍 地圖」按鈕展開地圖，第一次展開才建立（省載入次數）
function dayMapToggle(card,date,bar,before){
  const pts=date==='9/16'?null:dayPts(date);
  if(pts&&!pts.length)return;
  const btn=document.createElement('button');btn.type='button';btn.className='mapbtn rt mt';btn.textContent='📍 地圖';
  bar.insertBefore(btn,bar.firstChild);
  const wrap=document.createElement('div');wrap.className='day-map';wrap.hidden=true;card.insertBefore(wrap,before);
  btn.addEventListener('click',e=>{
    e.stopPropagation();
    wrap.hidden=!wrap.hidden;btn.classList.toggle('on',!wrap.hidden);
    if(wrap.hidden||wrap.dataset.ready)return;
    wrap.dataset.ready='1';
    if(pts){wrap.innerHTML='<div class="gmap"></div>';mountMap(wrap.firstChild,pts);}
    else buildRunMap(wrap);
  });
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
  const rs=runSegments();
  [[rs.p1,'routes1'],[rs.am.slice(rs.p1.length),'routes2'],[rs.pm,'routes3']].forEach(([segs,id])=>{
    const h=document.getElementById(id);h.replaceWith(routesEl(segs));
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
    el.innerHTML='<div class="day-head"><span class="day-d">'+d[0]+' '+d[1]+'</span><span class="day-t">'+d[2]+'</span></div><ul class="day-tl"></ul>';
    const ul=el.querySelector('.day-tl');
    const rb=routesEl(daySegments(d[0]));el.insertBefore(rb,ul);
    dayMapToggle(el,d[0],rb,ul);
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
