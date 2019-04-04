var allow_notif_1on1_btn = document.getElementById('allow_notif_1on1_btn');
if (allow_notif_1on1_btn) {allow_notif_1on1_btn.onclick = askPermission;}


function log_notif_allowance(status_code) {

    var form_data = new FormData();
    form_data.append("status_code",status_code);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/1-on-1/push-notif/allow-attempt/');// url gotten from from urls_push_notif.py
    xhr.timeout = 15000; // time in milliseconds, i.e. 15 seconds
    xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.onload = function () {
        if (this.status == 200) {
          // log_notif_allowance('3');
          // var data = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
          // window.location.replace(data.redirect);
        } else {
          // e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
          throw new Error('Bad status code from server.');
          // window.location.replace('/1-on-1/push-notif/failure/subscription-action/');
        }
    };
    xhr.onerror = function () {
        // onerror fires when there is a failure on the network level
        throw new Error('Network error galore');
        // window.location.replace('/1-on-1/push-notif/failure/subscription-action/');
    };
    xhr.ontimeout = function (e) {
        // XMLHttpRequest timed out
        // window.location.replace('/1-on-1/push-notif/failure/subscription-action/');
        throw new Error('XMLHttpRequest timed out');
    };
    xhr.send(form_data);

}


function askPermission(e) {
	
	// error-handling cases
	// alert("maximized notif");
	var NotificationIsSupported = !!(window.Notification /* W3C Specification */ || window.webkitNotifications /* old WebKit Browsers */ || navigator.mozNotification /* Firefox for Android and Firefox OS */)
	// alert('before');
	if ((!NotificationIsSupported) || (!('serviceWorker' in navigator)) || (!('PushManager' in window))) return;
	// alert('after');
	e.preventDefault();

	return new Promise(function(resolve, reject) {
		var permissionResult = Notification.requestPermission(function(result) {
			// console.log('1')//third
			resolve(result);
		});

		if (permissionResult) {
			// console.log('2')//first
		  permissionResult.then(resolve, reject);
		  // console.log('8')
		}
		// console.log('3');//second
	})

	.then(function(permissionResult) {

	  if (permissionResult === 'denied') {
	  	// dim_screen('off');
	  	// console.log('The permission request was dismissed.');
	  	log_notif_allowance('1');
	  	// TODO: what happens if user accepts notifications for one sybil, and blocks them for another?
	  	window.location.replace('/push-notification/subscription/denied/');
		// return;
	  } else if (permissionResult === 'default') {
	  	// dim_screen('off');
		
		alert('Permission wasn\'t granted. Allow a retry.');
		// console.log('5');
		log_notif_allowance('2');
		// alert('hi');
		window.location.replace('/push-notification/subscription/temporarily-denied/');
		// return;
	  } else if (permissionResult === 'granted') {
		subscribeUserToPush();
		// dim_screen('off');
		// console.log('6');//fourth
		return;
	  } else {
	  	dim_screen('off');
		// console.log('Something went wrong');
		// console.log('7');
		return;
	  }

	});
}

function subscribeUserToPush() {

  var pub_key = document.getElementById("notif_pub_key");
  var service_worker_location = document.getElementById("sw_loc");
  return navigator.serviceWorker.register(service_worker_location.value)
  .then(function(registration) {
	var subscribeOptions = {
	  userVisibleOnly: true,
	  applicationServerKey: urlBase64ToUint8Array(pub_key.value)
	};
	return registration.pushManager.subscribe(subscribeOptions);
  })
  .then(function(pushSubscription) {
	// sendSubscriptionToBackEnd(pushSubscription);
	sendSubscriptionToServer(JSON.stringify(pushSubscription));
	return pushSubscription;
  });
}


// function sendSubscriptionToBackEnd(subscription) {
// 	var sub_obj =  {
// 		method: 'POST',
// 		headers: {
// 		  'Content-Type': 'application/json',
// 		  'X-CSRFToken':get_cookie('csrftoken'),
// 		  'X-Requested-With':'XMLHttpRequest'// ensure request.is_ajax() calls are possible in the python backend (those calls check for this header)
// 		},
// 		body: JSON.stringify(subscription)
// 	}
// 	return fetch('/subscription/save/', sub_obj)
// 	.then(function(response) {
// 		if (!response.ok) {
// 		  throw new Error('Bad status code from server.');
// 		} else {
// 			return response.json();
// 		}
// 	})
// 	.then(function(responseData) {
// 		// response from the server
// 		if (!(responseData.data && responseData.data.success)) {
// 		  throw new Error('Bad response from server.');
// 		}
// 	});
// }


function sendSubscriptionToServer(subscription) {
    // dim_screen('on','- sending notification -');
    dim_screen('on','- allowing notification -');
    var target_id = document.getElementById("allow_tid");
    var fts = document.getElementById("fts");
    var form_data = new FormData();
    var payload = JSON.parse(subscription);
    if (fts.value) {
		if (fts.value === '1') {
        	form_data.append("first_time_subscriber",'1')
    	}
    }
    form_data.append("endpoint", payload['endpoint']);
    form_data.append("auth", payload['keys']['auth']);
    form_data.append("p256dh", payload['keys']['p256dh']);
    form_data.append("target_id",target_id.value);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/push-notification/subscription/save/');// url gotten from from urls_push_notif.py
    xhr.timeout = 15000; // time in milliseconds, i.e. 15 seconds
    xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.onload = function () {
        if (this.status == 200) {
          // log_notif_allowance('3');
          var data = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
          window.location.replace(data.redirect);
        } else {
          // e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
          window.location.replace('/1-on-1/push-notif/failure/subscription-action/');
        }
    };
    xhr.onerror = function () {
        // onerror fires when there is a failure on the network level
        window.location.replace('/1-on-1/push-notif/failure/subscription-action/');
    };
    xhr.ontimeout = function (e) {
        // XMLHttpRequest timed out
        window.location.replace('/1-on-1/push-notif/failure/subscription-action/');
    };
    xhr.onprogress = function () {
        // if needed
    };
    xhr.send(form_data);
}


function get_cookie(name) {
  if (!name) { return null; }
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length >= 2) return parts.pop().split(";").shift();
}


function urlBase64ToUint8Array(base64String) {
	var padding = '='.repeat((4 - base64String.length % 4) % 4);
	var base64 = (base64String + padding)
		.replace(/\-/g, '+')
		.replace(/_/g, '/');

	var rawData = window.atob(base64);
	var outputArray = new Uint8Array(rawData.length);

	for (var i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}


function dim_screen(status, text) {
	if (status === 'on') {
		var overlay = document.createElement('div');
		overlay.id = "notif_overlay";
		overlay.className = 'ovl';//
		var parent = document.createElement('div');
		parent.id = "notif_preloader";
		parent.className = "outer_ldr";//
		var loader = document.createElement('div');
      	loader.className = 'ldr ma';//
      	var caption = document.createElement('div');
      	caption.id = "preloader_message";
      	caption.className = "cap sp cs cgy mbl";//
      	caption.insertAdjacentText('afterbegin',text);
		document.body.appendChild(overlay);
		document.body.appendChild(parent);
		parent.insertAdjacentElement('afterbegin',loader);
      	parent.insertAdjacentElement('afterbegin',caption);
		document.body.style.overflow = 'hidden';
	}
	if (status === 'off') {
		var overlay = document.getElementById("notif_overlay");
		var parent = document.getElementById("notif_preloader");
		if (overlay) {overlay.parentNode.removeChild(overlay);}
		if (parent) {parent.parentNode.removeChild(parent);}
		document.body.style.overflow = 'visible';
	}
}

////////////////////////////////////////////////////////////////

var notif_sending_btn = document.getElementById('send_notif_1on1_btn');
if (notif_sending_btn) {notif_sending_btn.onclick = sendNotif;}

function sendNotif(e){
	e.preventDefault();

	var target_id = document.getElementById("send_tid");
	if (!target_id.value) {
		window.location.replace('/push-notification/subscription/malformed-target/');
	} else {
		dim_screen('on','- sending notification -');
		var form_data = new FormData();
		form_data.append("tid",target_id.value);
		form_data.append("dec",'1');
		var xhr = new XMLHttpRequest();
		xhr.open('POST', '/1-on-1/push-notif/send/');// url gotten from from urls_push_notif.py
		xhr.timeout = 35000; // time in milliseconds, i.e. 15 seconds
		xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xhr.onload = function () {
			var resp = JSON.parse(this.responseText);
			if (this.status == 200) {
			  // var resp = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
			  window.location.replace(resp.redirect);
			} else {
			  // e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
			  window.location.replace(resp.redirect);
			}
		};
		xhr.onerror = function () {
			// onerror fires when there is a failure on the network level
			window.location.replace('push-notification/subscription/unavailable/');
			// dim_screen('off');
		};
		xhr.ontimeout = function (e) {
			// XMLHttpRequest timed out
			window.location.replace('push-notification/subscription/unavailable/');
			// dim_screen('off');
		};
		xhr.onprogress = function () {
			// if needed
		};
		xhr.send(form_data);
	}
}