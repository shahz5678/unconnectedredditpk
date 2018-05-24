var share_btns = document.getElementsByClassName('wa-sharing');
for (var i=0, len=share_btns.length; i < len; i++) share_btns[i].onclick = log_click;

function get_csrf_cookie(name) {
  if (!name) { return null; }
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length >= 2) return parts.pop().split(";").shift();
}

function log_click(e) {
  var form_data = new FormData();
  form_data.append("pid",this.getAttribute('data-pid'));
  form_data.append("sid",this.getAttribute('data-sid'));
  form_data.append("oid",this.getAttribute('data-oid'));
  form_data.append("st",this.getAttribute('data-st'));
  form_data.append("org",this.getAttribute('data-org'));
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/log-share/');// give target url
  xhr.timeout = 30000; // time in milliseconds, i.e. 30 seconds
  xhr.setRequestHeader("X-CSRFToken", get_csrf_cookie('csrftoken'));
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
  // xhr.onload = function () {
  //   if (this.status == 200) {
  //     var resp = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
  //     window.location.replace(resp.message);//supported
      
  //   } else {
  //     // e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
  //     window.location.replace('/missing/');
      
  //   }
  // };
  // xhr.onerror = function () {
  //   // onerror fires when there is a failure on the network level
  //   window.location.replace(fail_url);// e.g. fail_url = '/private_chat/'
    
  // };
  // xhr.onprogress = function () {
    
  // }
  // xhr.ontimeout = function (e) {
  //   // XMLHttpRequest timed out
  //   window.location.replace(fail_url);
    
  // };
  xhr.send(form_data);
}