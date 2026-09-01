const ALL=[...P1.map((d,i)=>[d,'a'+i]),...P2.map((d,i)=>[d,'b'+i]),...P3.map((d,i)=>[d,'c'+i])];
const SPRITE=n=>'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/'+n+'.png';
let done=new Set();
const KEY='tokyo2026:done';

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

function render(){
  const r1=document.getElementById('rail1'),r2=document.getElementById('rail2'),r3=document.getElementById('rail3');
  r1.innerHTML='';r2.innerHTML='';r3.innerHTML='';
  P1.forEach((d,i)=>r1.appendChild(stopEl(d,'a'+i,i+1)));
  P2.forEach((d,i)=>r2.appendChild(stopEl(d,'b'+i,P1.length+i+1)));
  P3.forEach((d,i)=>r3.appendChild(stopEl(d,'c'+i,P1.length+P2.length+i+1)));

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
    const tl=d[3].map(it=>
      '<li'+(it[2]?' class="key"':'')+'><span class="tl-t">'+it[0]+'</span><span>'+it[1]+'</span></li>'
    ).join('');
    el.innerHTML='<div class="day-head"><span class="day-d">'+d[0]+' '+d[1]+'</span><span class="day-t">'+d[2]+'</span></div><ul class="day-tl">'+tl+'</ul>';
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
}

document.getElementById('reset').addEventListener('click',()=>{
  done.clear();saveDone();
  document.querySelectorAll('.stop.done').forEach(e=>e.classList.remove('done'));
  updateBar();
});

document.querySelectorAll('.nav button').forEach(b=>{
  b.addEventListener('click',()=>{
    document.querySelectorAll('.nav button').forEach(x=>x.classList.toggle('on',x===b));
    document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v.id==='v-'+b.dataset.v));
    window.scrollTo(0,0);
  });
});

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
render();
loadDex();

if('serviceWorker' in navigator){
  navigator.serviceWorker.register('sw.js').catch(()=>{/* 註冊失敗不影響使用 */});
}
