{% load staticfiles %}

self.addEventListener('push', function(event) {
  console.log('[Service Worker] Push Received.');
  console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);
  self.data = JSON.parse(event.data.text());
  const title = 'Oly-Exams Notification';
  const options = {
    body: self.data['body'],
    icon: '{% static "logo_square.png" %}',
    //badge: event.data['badge']
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  console.log('[Service Worker] Notification click Received.');

  event.notification.close();
  if(self.data['url']){
    event.waitUntil(
      clients.openWindow(self.data['url'])
    );
  }
});
