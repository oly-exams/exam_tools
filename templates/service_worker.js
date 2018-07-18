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
  clients.matchAll({includeUncontrolled: true}).then(function(clientsArr){
    console.log(clientsArr);
    return new Promise(function(resolve){
      var cli = 0;
      for (i = 0; i < clientsArr.length; i++) {
        const url = new URL(clientsArr[i].url);
        if (url.pathname === self.data['url']) {
            cli = clientsArr[i];
            resolve(cli);
          }
        }
      resolve(0);
    })
  }).then(function(cli){
    if (cli === 0) {
    }else{
      if (self.data['reload_client']) {
        //TODO: test
        console.log('sending reload message');
        cli.postMessage("reload");
      }
    }
  })
  );
});

self.addEventListener('notificationclick', function(event) {
  console.log('[Service Worker] Notification click Received.');
  event.waitUntil(
    clients.matchAll({includeUncontrolled: true}).then(function(clientsArr){
      console.log(clientsArr);
      return new Promise(function(resolve){
        var found = false;
        var cli = 0;
        for (i = 0; i < clientsArr.length; i++) {
          console.log(clientsArr[i].url);
          const url = new URL(clientsArr[i].url);
          if (url.pathname === self.data['url']) {
              // We already have a window to use, focus it.
              console.log('found');
              found = true;
              cli = clientsArr[i];
              resolve(cli);
            }
          }
        resolve(0);
      })
    }).then(function(cli){
      if (cli === 0) {
        console.log('not found, opening');
        console.log(self.data['url']);
        // Create a new window.
        event.waitUntil(
          console.log(clients.openWindow(self.data['url']))
        );
      }else{
        //if (self.data['reload_client']) {
        //  console.log('sending reload message');
        //  cli.postMessage("reload");
        }
        console.log('focus');
        event.waitUntil(
          console.log(cli.focus())
        );
      }
    })
  );
});
