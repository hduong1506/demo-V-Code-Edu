// V-Code Edu Service Worker — Network-First (luôn cập nhật ngay khi bạn sửa code, tự chạy Cache khi mất mạng)
const CACHE_NAME = 'vcode-edu-v5';
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './css/design-system.css',
  './js/lessons-data.js',
  './js/three-hero.js',
  './js/scratch-bridge.js',
  './js/ide-engine.js',
  './js/ai-tutor.js',
  './js/realtime-monitor.js',
  './js/offline-db.js',
  './js/app.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(CORE_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
