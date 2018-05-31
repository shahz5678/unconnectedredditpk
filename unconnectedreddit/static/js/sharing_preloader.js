// feeder for sharing_preloader.v1.1.js
// Compress via https://jscompress.com/ and press "download"
var share_btns = document.getElementsByClassName('share');
if (share_btns) {
	share_btns[0].onclick = show_pre;
	share_btns[1].onclick = show_pre;
}

function personal_group_preloader(action) { 
    switch (action) {
     case "create":    
      var overlay = document.createElement('div');
      overlay.id = "personal_group_overlay";
      overlay.className = 'ovl';//
      var parent = document.createElement('div');
      parent.id = "personal_group_preloader";
      parent.className = "outer_ldr";//
      var loader = document.createElement('div');
      loader.className = 'ldr ma';//
      var caption = document.createElement('div');
      caption.id = "preloader_message";
      caption.className = "cap sp cs cgy mbl";//
      caption.insertAdjacentText('afterbegin','- sharing foto -');
      document.body.appendChild(overlay);
      document.body.appendChild(parent);
      parent.insertAdjacentElement('afterbegin',loader);
      parent.insertAdjacentElement('afterbegin',caption);
      document.body.style.overflow = 'hidden';
      break;
    case "destroy":
      var overlay = document.getElementById("personal_group_overlay");
      var parent = document.getElementById("personal_group_preloader");
      if (overlay) {overlay.parentNode.removeChild(overlay);}
      if (parent) {parent.parentNode.removeChild(parent);}
      document.body.style.overflow = 'visible';
      break;
    default:
      break;
    }
}

function show_pre(e){
  if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]") return;
	personal_group_preloader('create');
	window.onunload = function(){personal_group_preloader('destroy');};
}