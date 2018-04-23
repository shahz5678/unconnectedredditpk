// feeder for helper_funcs.v1.1.js
// Compress via https://jscompress.com/ and press "download"
var valid_img = false;
var max_img_width = 400;
var wranges = [max_img_width, Math.round(0.8*max_img_width), Math.round(0.6*max_img_width),Math.round(0.4*max_img_width),Math.round(0.2*max_img_width)];

var pg_form = document.getElementById('personal_group_form')
if (pg_form) {pg_form.onsubmit = personal_group_submit;};
var browse_image_btn = document.getElementById('browse_image_btn');//supported
if (browse_image_btn) {browse_image_btn.onchange = show_image_name;}

function detect_android_ver(){

  var ua = navigator.userAgent;
  if( ua.indexOf("Android") >= 0 )
  {
    var androidversion = parseFloat(ua.slice(ua.indexOf("Android")+8)); 
    return androidversion;
  } else {
    return 100;
  }
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
      caption.innerHTML = '- resizing foto -';
      document.body.appendChild(overlay);
      document.body.appendChild(parent);
      parent.insertAdjacentElement('afterbegin',loader);
      parent.insertAdjacentElement('afterbegin',caption);
      document.body.style.overflow = 'hidden';
      // var overlay = document.createElement('div');
      // overlay.id = "personal_group_overlay";
      // overlay.className = 'ovl';//
      // var parent = document.createElement('div');
      // parent.id = "personal_group_preloader";
      // parent.className = "outer_ldr";//
      // var loader = document.createElement('div');
      // loader.className = 'ldr ma';//
      // loader.innerHTML = '<hr><hr><hr><hr>';//
      // var caption = document.createElement('div');
      // caption.id = "preloader_message";
      // caption.className = "cap sp cs cgy mbl";//
      // caption.innerHTML = '- resizing foto -';
      // document.body.appendChild(overlay);
      // document.body.appendChild(parent);
      // parent.insertAdjacentElement('afterbegin',loader);
      // parent.insertAdjacentElement('afterbegin',caption);
      // document.body.style.overflow = 'hidden';
      break;
    case "update":
      var caption = document.getElementById("preloader_message");
      if (caption) {caption.innerHTML = '- posting foto -';}
      break;
    case "finishing":
      var caption = document.getElementById("preloader_message");
      if (caption) {caption.innerHTML = '- finishing -';}
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

function show_image_name(e) { 
  // if opera mini, do nothing
  if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]"  || !e.target.files) return;//supported
	
  document.getElementById('main_cam').style.display = 'none';
  var filename = document.getElementById('filename');
  filename.innerHTML = e.target.value.replace(/^.*[\\\/]/, '').slice(0,20);
	filename.style.display = 'block';

  if (e.target.files[0].size < 20000001){ // don't allow files bigger than 20000000 Bytes (20 MB), since that is the server-side (nginx) limit as well
		if (window.FileReader && window.Blob){
			// Filereader is supported, Blob is polyfilled (to include BlobBuilder)
      validate_img_file(e);
		}
	} else {
		throw_err(e.target,'size','pg_main');
	}
}

// grab the file from the input and process it
function validate_img_file(e) {
  if (is_pub_grp_img) {
    pub_grp_subform.disabled = true;
  } else if (is_pub_img) {
    pub_img_subform.disabled = true;
  } else if (is_reply) {
    rep_subform.disabled = true;
  } else {
    subform.disabled = true;
  };
  var file = e.target.files[0];
  // try using createobjecturl() instead, and then fallback to file reader (see https://hacks.mozilla.org/2011/01/how-to-develop-a-html5-image-uploader/)
  var reader = new FileReader();//supported
  // a FileReader is async (which means that your program will not stall whilst a file is being read), so we pass the actual checking script as the onload handler
  reader.onload = validate_file;//
  reader.readAsArrayBuffer(file.slice(0,4));// instead of slice(0,25)
}

function validate_file(e) {
  var header = "";
  var arr = new Uint8Array(e.target.result);//supported
  for(var i = 0; i < arr.length; i++) {
     header += arr[i].toString(16);
  }
  switch (header) {
	case "89504e47":    
    if (is_pub_grp_img) {valid_pub_grp_img='png';} else if (is_pub_img) {valid_public_img = 'png';} else if (is_reply) {valid_rep_img='png';} else {valid_img = 'png';}
    break;
	case "47494638":
    if (is_pub_grp_img) {valid_pub_grp_img='gif';} else if (is_pub_img) {valid_public_img = 'gif';} else if (is_reply) {valid_rep_img = 'gif';} else {valid_img = 'gif';}
    break;
	case "ffd8ffe0":
  case "ffd8ffe1":
  case "ffd8ffe2":
  case "ffd8ffe3":
	case "ffd8ffe8":
  case "ffd8ffdb":
	  if (is_pub_grp_img) {valid_pub_grp_img='jpeg';} else if (is_pub_img) {valid_public_img = 'jpeg';} else if (is_reply) {valid_rep_img = 'jpeg';} else {valid_img = 'jpeg';}
    break;
	default:
    if (is_pub_grp_img) {
      // valid_pub_grp_img = null;
      throw_err(pub_grp_browse_image_btn,'mime','pub_grp_img')
    } else if (is_pub_img) {
      valid_public_img = null;
      throw_err(browse_pub_img_btn,'mime','public_img');
    } else if (is_reply) {
      // public group direct response
      valid_rep_img = null; //null signifies that image is 'undefined', i.e. not an image file
      throw_err(browse_rep_image_btn,'mime','pg_reply');
    } else {
      // public group main
      throw_err(browse_image_btn,'mime','pg_main');
    }
    break;
    }
  if (is_pub_grp_img) {
    pub_grp_subform.disabled = false;
    is_pub_grp_img = false;
  } else if (is_pub_img) {
    pub_img_subform.disabled = false;
    is_pub_img = false;
  }else if (is_reply) {
    rep_subform.disabled = false;
    is_reply = false;
  } else {
    subform.disabled = false;
  }
}

function process_ajax(text, img_name, target_action, img_to_send, is_resized, is_reoriented, type, img_field, reply_field, fail_url){
  // create and populate the form with data
  var form_data = new FormData();
  if (text) {form_data.append(reply_field, text);}
  if (is_resized) {form_data.append("resized", '1');}
  if (is_reoriented) {form_data.append("reoriented", '1');}
  if (type === 'pg_main') {
    // uploading from private chat
    form_data.append("tid",document.getElementById('tid').value);
    form_data.append("sk",document.getElementById('sk').value);
  } else if (type === 'public_img') {
    // originating from upload_public_photo
    form_data.append("sk",document.getElementById('pub_img_sk').value);
  } else if (type === 'pg_reply') {
    // uploading from private chat (direct response)
    if (rep_payload) form_data.append("pl", rep_payload);
  } else {
    // uploading from public group
    form_data.append("gp",document.getElementById('pub_grp_subform').value);
    form_data.append("sk",document.getElementById('pub_grp_sk').value);
  }; 
  form_data.append(img_field, img_to_send, img_name);
  personal_group_preloader('update');
  // send the form via AJAX
  var xhr = new XMLHttpRequest();
  xhr.open('POST', target_action);
  xhr.timeout = 45000; // time in milliseconds, i.e. 45 seconds
  xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

  xhr.onload = function () {
    if (this.status == 200) {
      var resp = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
      window.location.replace(resp.message);//supported
      personal_group_preloader('destroy');
    } else {
      // e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
      window.location.replace('/missing/');
      personal_group_preloader('destroy');
    }
  };
  xhr.onerror = function () {
    // onerror fires when there is a failure on the network level
    window.location.replace(fail_url);// e.g. fail_url = '/private_chat/'
    personal_group_preloader('destroy');
  };
  xhr.onprogress = function () {
    personal_group_preloader('finishing');
  }
  xhr.ontimeout = function (e) {
    // XMLHttpRequest timed out
    window.location.replace(fail_url);
    personal_group_preloader('destroy');
  };
  xhr.send(form_data);
}


function personal_group_submit(e) {
  if (!browse_image_btn.files[0] || !valid_img || detect_android_ver() < 4.1) return;
  // block the default behavior
  e.preventDefault();
  personal_group_preloader('create');
  // prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
  prep_image(browse_image_btn.files[0],text_field.value, browse_image_btn.files[0].name, e.target.action, 'pg_main','image', 'reply', '/private_chat/', null, process_ajax);
}

function prep_image(src_img, text, img_name, target_action, type, img_field, reply_field, fail_url, target_size, callback) {	
  get_orientation(src_img, type, function(orientation) {
    var img = document.createElement('img');
    var fr = new FileReader();//supported
    fr.onload = function(){
      var dataURL = fr.result;
      img.onload = function(){
        img_width = this.width;
        img_height = this.height;
        img_to_send = resize_and_compress(this, img_width, img_height, "image/jpeg", orientation, target_size);//, 100);
        if (img_to_send.size > src_img.size){
          callback(text, img_name, target_action, src_img, false, false, type, img_field, reply_field, fail_url);
        } else {
          callback(text, img_name, target_action, img_to_send, true, true, type, img_field, reply_field, fail_url);
        }
      }
      img.onerror = function () {
        window.location.href = window.location.href;
        personal_group_preloader('destroy');
      }
      img.src = dataURL;
    }
    fr.readAsDataURL(src_img);//supported
  });
}


function resize_and_compress(source_img, img_width, img_height, mime_type, orientation, target_size){
  // flip width and height (when needed)
  switch (orientation) {
    case 2:
    case 3:
    case 4:
      break;
    case 5:
    case 6:
    case 7:
    case 8:
      var temp_width = null;
      temp_width = img_width;
      img_width = img_height;
      img_height = temp_width;
      break;
    default:
      break;
  }

  var new_width = null;
  if (target_size) {
    new_width = target_size;
  } else {
    switch (true) {
    case img_width < wranges[4]: new_width = wranges[4]; break;
    case img_width < wranges[3]: new_width = wranges[4]; break;
    case img_width < wranges[2]: new_width = wranges[3]; break;
    case img_width < wranges[1]: new_width = wranges[2]; break;
    case img_width < wranges[0]: new_width = wranges[1]; break;
    default: new_width = wranges[0]; break;
    }
  };

  var wpercent = (new_width/img_width);
  var new_height = Math.round(img_height*wpercent);// maintaining aspect ratio

  var canvas = document.createElement('canvas');
  canvas.width = new_width;
  canvas.height = new_height;

  var ctx = canvas.getContext('2d');
  // see for guidance: https://github.com/blueimp/JavaScript-Load-Image/blob/master/js/load-image-orientation.js
   switch (orientation) {
    case 2: 
      ctx.translate(new_width, 0);
      ctx.scale(-1, 1);
      break;//supported
    case 3:
      // rotate 180 degrees left
      ctx.translate(new_width, new_height);
      ctx.rotate(-Math.PI);
      break;//supported
    case 4: 
      // vertical flip
      ctx.translate(0, new_height);
      ctx.scale(1, -1);
      break;//supported
    case 5: 
      // vertical flip + 90 rotate right
      ctx.rotate(0.5 * Math.PI);
      ctx.scale(new_height/new_width,-new_width/new_height);
      break;//supported
    case 6: 
      // rotate 90 degrees right
      ctx.rotate(0.5 * Math.PI);
      ctx.translate(0, -new_width);
      ctx.scale(new_height/new_width,new_width/new_height);
      break;//supported
    case 7:
      // horizontal flip + 90 rotate right
      ctx.rotate(0.5 * Math.PI);
      ctx.translate(new_height, -new_width);
      ctx.scale(-new_height/new_width,new_width/new_height);
      break;
    case 8: 
      // rotate 90 degrees left
      ctx.translate(0, new_height);
      ctx.scale(new_width/new_height,new_height/new_width);
      ctx.rotate(-0.5 * Math.PI);
      break;
    default: 
      break;
  }

  ctx.drawImage(source_img, 0, 0, new_width, new_height);
  return dataURItoBlob(canvas.toDataURL(mime_type),mime_type);
}


// converting image data uri to a blob object
function dataURItoBlob(dataURI,mime_type) {
  var byteString = atob(dataURI.split(',')[1]);//supported
  var ab = new ArrayBuffer(byteString.length);//supported
  var ia = new Uint8Array(ab);//supported
  for (var i = 0; i < byteString.length; i++) { ia[i] = byteString.charCodeAt(i); }//supported
  return new Blob([ab], { type: mime_type });//supported
}

function get_cookie(name) {
  if (!name) { return null; }
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length >= 2) return parts.pop().split(";").shift();
}


function throw_err(file_target,type,which_section) {
	if (which_section == 'pub_grp_img') {
    if (type == 'size') {var target_elem = document.getElementById("pub_grp_img_size_err");} else {var target_elem = document.getElementById("pub_grp_img_mime_err");}
    pub_grp_form.insertAdjacentElement('afterbegin',target_elem);
  } else if (which_section == 'public_img') {
    if (type == 'size') {var target_elem = document.getElementById("pub_img_size_err");} else {var target_elem = document.getElementById("pub_img_mime_err");}
    public_photo_form.insertAdjacentElement('afterbegin',target_elem);
  } else if (which_section == 'pg_reply') {
    if (type == 'size') {var target_elem = document.getElementById("pg_rep_size_err");} else {var target_elem = document.getElementById("pg_rep_mime_err");}
    form_template.insertAdjacentElement('afterbegin',target_elem);
  } else {
    var top_elem = document.getElementById("personal_group_top");
  	if (type == 'size') {var target_elem = document.getElementById("pg_size_err");} else {var target_elem = document.getElementById("pg_mime_err");}
  	if (top_elem) {
      top_elem.innerHTML = '';
    	top_elem.insertAdjacentElement('afterbegin',target_elem);
    };
  }
  target_elem.style.display = null;
  file_target.value = "";
}

// used to determine orientation information
function get_orientation(file, type, callback) {
  if (type === 'pg_reply') {
    if (valid_rep_img!='jpeg') {return callback(-2);};
  } else if (type === 'pub_grp_img') {
    if (valid_pub_grp_img!='jpeg') {return callback(-2);};
  } else if (type === 'public_img') {
    if (valid_public_img!='jpeg') {return callback(-2);};
  } else {
    // type === 'pg_main'. If any new types are created, add more if-else statements.
    if (valid_img!='jpeg') {return callback(-2);};
  }
  var reader = new FileReader();
  reader.onload = function(e) {
    var view = new DataView(e.target.result);
    if (view.getUint16(0, false) != 0xFFD8) return callback(-2);
    var length = view.byteLength, offset = 2;
    while (offset < length) {
      if (view.getUint16(offset+2, false) <= 8) return callback(-1);
      var marker = view.getUint16(offset, false);
      offset += 2;
      if (marker == 0xFFE1) {
        if (view.getUint32(offset += 2, false) != 0x45786966) return callback(-1);
        var little = view.getUint16(offset += 6, false) == 0x4949;
        offset += view.getUint32(offset + 4, little);
        var tags = view.getUint16(offset, little);
        offset += 2;
        for (var i = 0; i < tags; i++)
          if (view.getUint16(offset + (i * 12), little) == 0x0112)
            return callback(view.getUint16(offset + (i * 12) + 8, little));
      }
      else if ((marker & 0xFF00) != 0xFF00) break;
      else offset += view.getUint16(offset, false);
    }
    return callback(-1);
  };
  reader.readAsArrayBuffer(file.slice(0, 128 * 1024));
}

// polyfill for Blob()
Blob = (function() {
  var nativeBlob = Blob;

  // Add unprefixed slice() method.
  if (Blob.prototype.webkitSlice) {
    Blob.prototype.slice = Blob.prototype.webkitSlice;  
  }
  else if (Blob.prototype.mozSlice) {
    Blob.prototype.slice = Blob.prototype.mozSlice;  
  }

  // Temporarily replace Blob() constructor with one that checks support.
  return function(parts, properties) {
    try {
      // Restore native Blob() constructor, so this check is only evaluated once.
      Blob = nativeBlob;
      return new Blob(parts || [], properties || {});
    }
    catch (e) {
      // If construction fails provide one that uses BlobBuilder.
      Blob = function (parts, properties) {
        var bb = new (WebKitBlobBuilder || MozBlobBuilder), i;
        for (i in parts) {
          bb.append(parts[i]);
        }
        return bb.getBlob(properties && properties.type ? properties.type : undefined);
      };
    }        
  };
}());

////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Direct Response in Private Chat (JS functionality)


// var form_template = document.querySelector('#form_template');//supported
// if (form_template) {form_template.onsubmit = personal_group_reply_submit;};


// var rep_btns = document.querySelectorAll('button.rep');
// var browse_btns = document.querySelectorAll('input.rep');
// console.log(browse_btns);
// for (var i=0, len=rep_btns.length; i < len; i++) rep_btns[i].onclick = toggle_rep;
// for (var i=0, len=browse_btns.length; i < len; i++) {
//   console.log(i);
//   console.log(browse_btns[i]);
//   browse_btns[i].onchange = show_rep_image_name;
// }

// var browse_rep_image_btn = document.getElementById('browse_rep_image_btn');
// if (browse_rep_image_btn) {browse_rep_image_btn.onchange = show_rep_image_name;}

// Array.from(rep_btns).forEach(btn => btn.onclick = toggle_rep);//supported
// for (var i=0, len=rep_btns.length; i < len; i++) rep_btns[i].onclick = toggle_rep;

var is_reply = false;
var valid_rep_img = false;
var rep_payload = null;

function show_rep_image_name(e) { 
  // if opera mini, do nothing
  if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.target.files) return;
  var filename = e.target.value.replace(/^.*[\\\/]/, '').slice(0,20);
  var target_form = e.target.form;
  var rep_filename = target_form.querySelector('#rep_filename');
  var camera_icon =  target_form.querySelector('#rep_cam');
  var ok_btn = target_form.querySelector('#rep_ok_btn');
  var modal_top = target_form.querySelector('#modal_top');
  ok_btn.disabled = true;
  if (e.target.files[0].size < 20000001){ // don't allow files bigger than 20000000 Bytes (20 MB), since that is the server-side (nginx) limit as well
    if (window.FileReader && window.Blob){
      // is_reply = true;
      // validate_img_file(e);
      var file = e.target.files[0];
      var reader = new FileReader();//supported
      reader.onload = function(e){
          var header = "";
          var arr = new Uint8Array(e.target.result);//supported
          for(var i = 0; i < arr.length; i++) {
             header += arr[i].toString(16);
          }
          switch (header) {
            case "89504e47":
              valid_rep_img='png';
              modal_top.className = "sp cs mbs cgy";//
              modal_top.innerHTML = 'Jawab:';
              ok_btn.onclick = personal_group_reply_submit;
              ok_btn.disabled = false;
              break;
            case "47494638":
              valid_rep_img = 'gif';
              modal_top.className = "sp cs mbs cgy";//
              modal_top.innerHTML = 'Jawab:';
              ok_btn.onclick = personal_group_reply_submit;
              ok_btn.disabled = false;
              break;
            case "ffd8ffe0":
            case "ffd8ffe1":
            case "ffd8ffe2":
            case "ffd8ffe3":
            case "ffd8ffe8":
            case "ffd8ffdb":
              valid_rep_img = 'jpeg';
              modal_top.className = "sp cs mbs cgy";//
              modal_top.innerHTML = 'Jawab:';
              ok_btn.onclick = personal_group_reply_submit;
              ok_btn.disabled = false;
              break;
            default:
              valid_rep_img = null;
              modal_top.className = "cr lsp";//
              modal_top.innerHTML = 'Ye foto kharab hai, koi aur chunein';
              break;
          }
          rep_filename.innerHTML = filename;
          camera_icon.style.display = 'none';
          rep_filename.style.display = 'flex';
        };//validate_file;
      reader.readAsArrayBuffer(file.slice(0,4));// instead of slice(0,25)
    }
  } else {
    valid_rep_img = null;
    modal_top.className = "cr lsp";//
    modal_top.innerHTML = 'Ye foto buhut barri hai, choti foto chunein';
  }

}


function personal_group_reply_submit(e) {
  if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || detect_android_ver() < 4.1) return;
  // This can preventDefault only if image is attached, otherwise do nothing
  if (valid_rep_img) {
    e.preventDefault();
    var target_form = e.target.form;
    var image_file = target_form.querySelector('#browse_rep_image_btn').files[0];
    var rep_text = target_form.querySelector('#rep_text_field').value;
    var target_action = target_form.action;
    rep_payload = e.target.value;

    personal_group_preloader('create');
    // prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
    prep_image(image_file,rep_text, image_file.name, target_action, 'pg_reply','rep_image', 'rep_reply', '/private_chat/',null ,process_ajax);
  } else {
    if (valid_rep_img == null) {
      e.preventDefault();
      return;
    } else {
      return;
    }
  }
}


/////////////////////////////////////////////////////////
// Uploading Public Photos (JS functionality)
var is_pub_img = false;
var valid_public_img = false;
var public_photo_form = document.getElementById('public_photo_form');//supported
if (public_photo_form) {public_photo_form.onsubmit = public_photo_submit;};
var public_photo_upload_btn = document.getElementById('browse_pub_img_btn');//supported
if (public_photo_upload_btn) {public_photo_upload_btn.onchange = validate_public_image;}

function validate_public_image(e) { 
  // if opera mini, do nothing
  if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.target.files) return;
  document.getElementById("pub_img_size_err").style.display = 'none';
  document.getElementById("pub_img_mime_err").style.display = 'none';
  if (e.target.files[0].size < 20000001){ // don't allow files bigger than 20000000 Bytes (20 MB), since that is the server-side (nginx) limit as well
    if (window.FileReader && window.Blob){
      is_pub_img = true;
      validate_img_file(e);
    }
  } else {
    valid_public_img = null;
    throw_err(e.target,'size','public_img');
  }
}

function public_photo_submit(e) {
  if (detect_android_ver() < 4.1) return;
  // This can preventDefault only if image is attached, otherwise do nothing
  if (valid_public_img) {
    e.preventDefault();
    personal_group_preloader('create');
    // prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
    prep_image(browse_pub_img_btn.files[0],pub_img_caption_field.value, browse_pub_img_btn.files[0].name, e.target.action, 'public_img','image_file', 'caption', '/upload_public_photo/',400,process_ajax);
  } else {
    if (valid_public_img == null) {
      e.preventDefault();
      return;
    } else {
      return;
    }
  }
};
/////////////////////////////////////////////////////////
// Uploading Photos in Public Mehfils (JS functionality)
var is_pub_grp_img = false;
var valid_pub_grp_img = false;
var pub_grp_form = document.getElementById('pub_grp_form');//supported
if (pub_grp_form) {pub_grp_form.onsubmit = pub_grp_form_submit;};
var pub_grp_browse_image_btn = document.getElementById('pub_grp_browse_image_btn');//supported
if (pub_grp_browse_image_btn) {pub_grp_browse_image_btn.onchange = validate_pub_grp_img;};

function validate_pub_grp_img(e) { 
  // if opera mini, do nothing
  if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.target.files) return;
  document.getElementById("pub_grp_img_size_err").style.display = 'none';
  document.getElementById("pub_grp_img_mime_err").style.display = 'none';
  if (e.target.files[0].size < 20000001){ // don't allow files bigger than 20000000 Bytes (20 MB), since that is the server-side (nginx) limit as well
    if (window.FileReader && window.Blob){
      is_pub_grp_img = true;
      validate_img_file(e);
    }
  } else {throw_err(e.target,'size','pub_grp_img');};
};

function pub_grp_form_submit(e) {
  if (detect_android_ver() < 4.1) return;
  // This can preventDefault only if image is attached, otherwise do nothing
  if (valid_pub_grp_img) {
    e.preventDefault();
    personal_group_preloader('create');
    // prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
    prep_image(pub_grp_browse_image_btn.files[0],pub_grp_text_field.value, pub_grp_browse_image_btn.files[0].name, e.target.action, 'pub_grp_img', 'image', 'text', '/mehfil/awami/',400,process_ajax);
  } else {return;};
};