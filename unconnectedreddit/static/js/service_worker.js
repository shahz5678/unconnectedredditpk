self.addEventListener('fetch', function(event) {});

//////////////////////////////////////////////////////
self.addEventListener('push', function(event) {
  var payload = event.data.json();
  log_notif_reception('1');
  const promiseChain = self.registration.showNotification(payload.title, {
      "body": payload.body,
      "icon": "/static/img/notification.svg",// an icon size of 192px or more is a safe bet.
      "badge": "/static/img/notification.svg",// a small monochrome icon appearing on the top tray in chrome in android (an image of 72px or more should be good)
      "image": "/static/img/og_image.svg",
      "vibrate": [500,110,500,110,450,110,200,110,170,40,450,110,200,110,170,40,500],
      "tag": payload.tag,// used to make notification unique or generalized
      "renotify": true,// good idea to do this for chat apps (and must use 'tag' with it)
      "silent": false,// you want your notifications to vibrate, not to be silent
      "requireInteraction": true,//force a notification to stay visible until the user interacts with it
      "timestamp":payload.time,
      });

  event.waitUntil(promiseChain);
});


// self.addEventListener('push', function(event) {
//   const analyticsPromise = pushReceivedTracking();
//   const pushInfoPromise = fetch('/api/get-more-data')
//     .then(function(response) {
//       return response.json();
//     })
//     .then(function(response) {
//       const title = response.data.userName + ' says...';
//       const message = response.data.message;

//       return self.registration.showNotification(title, {
//         body: message
//       });
//     });

//   const promiseChain = Promise.all([
//     analyticsPromise,
//     pushInfoPromise
//   ]);

//   event.waitUntil(promiseChain);
// });



//////////////////////////////////////////////////////
//////////////////////////////////////////////////////
//  just a test example
// self.addEventListener('push', function(event) {
//   if (event.data) {
//   } else {
//   }
// });
//////////////////////////////////////////////////////
// a more complete example
// self.addEventListener('push', function(event) {
//   const promiseChain = self.registration.showNotification('Hello, World.');

//   event.waitUntil(promiseChain);
// });
//////////////////////////////////////////////////////
//  A more complicated example with a network request for data and tracking the push event with analytics
// self.addEventListener('push', function(event) {
//   const analyticsPromise = pushReceivedTracking();// will make a network request to our analytics provider
//   const pushInfoPromise = fetch('/api/get-more-data')
//     .then(function(response) {
//       return response.json();
//     })
//     .then(function(response) {
//       const title = response.data.userName + ' says...';
//       const message = response.data.message;

//       return self.registration.showNotification(title, {
//         body: message
//       });
//     });

//   const promiseChain = Promise.all([
//     analyticsPromise,
//     pushInfoPromise
//   ]);

//   event.waitUntil(promiseChain);
// });
///////////////////////////////////////////

function log_notif_reception(status_code) {
  fetch('/1-on-1/push-notif/received/', {
    "method": 'POST',
    "headers": {
      'Accept': 'application/json',
      'Content-Type':'application/json'//'application/x-www-form-urlencoded',//'application/json',
      // 'X-Requested-With': 'XMLHttpRequest',
    },
    "credentials": 'include',
    "body": JSON.stringify({'status_code':status_code})

  })
  .then(function(response) {
    if (!response.ok) {
      throw new Error('Bad status code from server.');
    }
  });

}

///////////////////////////////////////////////
// When notification is clicked

self.addEventListener('notificationclick', function(event) {
  const clickedNotification = event.notification;
  clickedNotification.close();

  // Do something (e.g. open a page, or just redirect to it if is already open) as the result of the notification click
  const rediretPage = '/1-on-1/friends/';
  const urlToOpen = new URL(rediretPage, self.location.origin).href;

  const promiseChain = clients.matchAll({
    type: 'window',
    includeUncontrolled: true
  })
  .then((windowClients) => {
    let matchingClient = null;

    for (let i = 0; i < windowClients.length; i++) {
      const windowClient = windowClients[i];
      if (windowClient.url === urlToOpen) {
        matchingClient = windowClient;
        break;
      }
    }

    if (matchingClient) {
      log_notif_reception('2')
      return matchingClient.focus();
    } else {
      log_notif_reception('3')
      return clients.openWindow(urlToOpen);
    }
  });

  event.waitUntil(promiseChain);


});
///////////////////////////////////////////////
// When notification is crossed or swiped away
// self.addEventListener('notificationclose', function(event) {
//   const dismissedNotification = event.notification;

//   event.waitUntil(promiseChain);
// });


