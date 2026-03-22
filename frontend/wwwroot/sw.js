const CACHE_NAME = 'recipitto-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/fonts.css',
  '/css/base.css',
  '/css/layout.css',
  '/css/spinner.css',
  '/css/index.css',
  '/css/search.css',
  '/css/recipe.css',
  '/css/recipe_edit.css',
  '/css/profile.css',
  '/css/admin.css',
  '/fonts/PTSans-Regular.ttf',
  '/fonts/PTSans-Bold.ttf',
  '/fonts/PTSans-Italic.ttf',
  '/fonts/PTSans-BoldItalic.ttf',
  '/dist/main.js',
  '/manifest.json',
];

// TODO: update cache in online mode

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});