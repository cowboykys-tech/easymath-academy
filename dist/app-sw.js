const CACHE = "easymath-app-shell-v2";
const STATIC = [
  "/offline.html",
  "/",
  "/index.html",
  "/styles.css?v=14",
  "/app.js?v=18",
  "/owner-login.html",
  "/owner-login.css?v=1",
  "/owner-login.js?v=1",
  "/teacher.html",
  "/teacher.css?v=10",
  "/teacher.js?v=10",
  "/kiosk.html",
  "/kiosk.css?v=1",
  "/kiosk.js?v=2",
  "/pwa.js?v=1",
  "/owner.webmanifest",
  "/teacher.webmanifest",
  "/kiosk.webmanifest",
  "/owner-icon.svg",
  "/teacher-icon.svg",
  "/kiosk-icon.svg",
  "/owner-icon-192.png",
  "/owner-icon-512.png",
  "/teacher-icon-192.png",
  "/teacher-icon-512.png",
  "/kiosk-icon-192.png",
  "/kiosk-icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(STATIC)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/auth/") || url.pathname.startsWith("/media/")) return;

  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request).catch(() => caches.match("/offline.html")));
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        const copy = response.clone();
        caches.open(CACHE).then(cache => cache.put(event.request, copy));
        return response;
      })
      .catch(() => caches.match(event.request, { ignoreSearch: true }))
  );
});
