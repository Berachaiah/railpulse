self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  self.clients.claim();
});

self.addEventListener('push', (event) => {
  let payload = {};
  try {
    payload = event.data.json();
  } catch (e) {
    payload = { body: event.data ? event.data.text() : '' };
  }

  // FCM data-only messages can arrive either flat ({title, body, url})
  // or wrapped one level deeper ({data: {title, body, url}, ...}) --
  // handle both shapes.
  const data = (payload.data && typeof payload.data === 'object') ? payload.data : payload;

  event.waitUntil(
    self.registration.showNotification(data.title || 'RailPulse', {
      body: data.body || '',
      icon: '/static/images/icon-192.png',
      badge: '/static/images/icon-192.png',
      data: { url: data.url || '/notifications' },
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/notifications')
  );
});
