// 快取策略：
// - 同源（頁面／stops.js／app.js）：網路優先，斷線才退回快取 → 資料永遠是最新的
// - 跨源（sprite／字體／PokeAPI）：先吃快取、背景更新 → 騎車時圖片秒開
const VER = 'tokyo2026-v2';
const CORE = [
  './',
  'index.html',
  'assets/styles.css',
  'assets/app.js',
  'data/stops.js',
  'assets/favicon.svg',
  'assets/icon-192.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VER).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VER).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const sameOrigin = new URL(e.request.url).origin === location.origin;

  if (sameOrigin || e.request.mode === 'navigate') {
    // 網路優先：成功就更新快取，失敗（斷線）退回快取
    // cache:'no-cache' 強制向伺服器重新驗證，避免被 HTTP 快取架空（沒變就 304，成本低）
    e.respondWith(
      fetch(e.request, { cache: 'no-cache' }).then(res => {
        const copy = res.clone();
        caches.open(VER).then(c => c.put(e.request, copy));
        return res;
      }).catch(() =>
        caches.match(e.request).then(hit => hit || caches.match('index.html'))
      )
    );
  } else {
    // 跨源資源：先吃快取、背景更新
    e.respondWith(
      caches.match(e.request).then(hit => {
        const update = fetch(e.request).then(res => {
          if (res.ok || res.type === 'opaque') {
            const copy = res.clone();
            caches.open(VER).then(c => c.put(e.request, copy));
          }
          return res;
        }).catch(() => hit);
        return hit || update;
      })
    );
  }
});
