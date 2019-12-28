// feeder for helper_funcs.v1.16.js
// Compress via https://jscompress.com/ and press "download"
var valid_img = false;
var max_img_width = 450;
var wranges = [max_img_width, Math.round(0.9*max_img_width),Math.round(0.8*max_img_width), Math.round(0.7*max_img_width),Math.round(0.6*max_img_width),Math.round(0.5*max_img_width),Math.round(0.4*max_img_width),Math.round(0.3*max_img_width),Math.round(0.2*max_img_width)];

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
			caption.insertAdjacentText('afterbegin','- resizing foto -');
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
	// filename.innerHTML = e.target.value.replace(/^.*[\\\/]/, '').slice(0,20);
	filename.insertAdjacentText('afterbegin',e.target.value.replace(/^.*[\\\/]/, '').slice(0,20));
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
	if (is_grp_img) {
		grp_subform.disabled = true;
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
	// alert(header);
	switch (header) {
	case "89504e47":    
		if (is_grp_img) {valid_grp_img='png';} else if (is_pub_img) {valid_public_img = 'png';} else if (is_reply) {valid_rep_img='png';} else {valid_img = 'png';}
		break;
	case "47494638":
		if (is_grp_img) {valid_grp_img='gif';} else if (is_pub_img) {valid_public_img = 'gif';} else if (is_reply) {valid_rep_img = 'gif';} else {valid_img = 'gif';}
		break;
	case "ffd8ffe0":
	case "ffd8ffe1":
	case "ffd8ffe2":
	case "ffd8ffe3":
	case "ffd8ffe8":
	case "ffd8ffdb":
	case "ffd8ffed":
		if (is_grp_img) {valid_grp_img='jpeg';} else if (is_pub_img) {valid_public_img = 'jpeg';} else if (is_reply) {valid_rep_img = 'jpeg';} else {valid_img = 'jpeg';}
		break;
	default:
		if (is_grp_img) {
			// valid_grp_img = null;
			throw_err(grp_browse_image_btn,'mime','grp_img')
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
	if (is_grp_img) {
		grp_subform.disabled = false;
		is_grp_img = false;
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
		form_data.append("aud",retrieve_audience());
		form_data.append("exp",retrieve_expiry());
		form_data.append("com",retrieve_comments());
		
	} else if (type === 'pg_reply') {
		// uploading from private chat (direct response)
		form_data.append("tt",rep_tt);
		form_data.append("bid",rep_bid);
		form_data.append("idx",rep_idx);
		form_data.append("tid",rep_tid);
		form_data.append("sk",rep_sk);
	} else {
		// uploading from public/private mehfil
		form_data.append("gp",document.getElementById('grp_subform').value);
		form_data.append("sk",document.getElementById('grp_sk').value);
		// form_data.append("wid",grp_writer_id);
	}; 
	form_data.append(img_field, img_to_send, img_name);
	personal_group_preloader('update');
	// send the form via AJAX
	var xhr = new XMLHttpRequest();
	xhr.open('POST', target_action);
	xhr.timeout = 55000; // time in milliseconds, i.e. 55 seconds
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
		window.location.replace(fail_url);// e.g. fail_url = '/1-on-1/'
		personal_group_preloader('destroy');
	};
	xhr.ontimeout = function (e) {
		// XMLHttpRequest timed out
		window.location.replace(fail_url);
		personal_group_preloader('destroy');
	};
	xhr.onprogress = function () {
		personal_group_preloader('finishing');
	};
	xhr.send(form_data);
}


function personal_group_submit(e) {
	if (!browse_image_btn.files[0] || !valid_img || detect_android_ver() < 4.1) return;
	// block the default behavior
	e.preventDefault();
	personal_group_preloader('create');
	// prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
	prep_image(browse_image_btn.files[0],text_field.value, browse_image_btn.files[0].name, e.target.action, 'pg_main','image', 'reply', '/1-on-1/', null, process_ajax);
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
		case img_width < wranges[8]: new_width = wranges[8]; break;
		case img_width < wranges[7]: new_width = wranges[8]; break;
		case img_width < wranges[6]: new_width = wranges[7]; break;
		case img_width < wranges[5]: new_width = wranges[6]; break;
		case img_width < wranges[4]: new_width = wranges[5]; break;
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
	if (which_section == 'grp_img') {
		if (type == 'size') {var target_elem = document.getElementById("grp_img_size_err");} else {var target_elem = document.getElementById("grp_img_mime_err");}
		grp_form.insertAdjacentElement('afterbegin',target_elem);
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
	} else if (type === 'grp_img') {
		if (valid_grp_img!='jpeg') {return callback(-2);};
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



	// var form_template = document.querySelector('#form_template');//select form in personal_group.html
var form_template = document.getElementById('form_template');
if (form_template) {
	// var rep_size = form_template.querySelector('#pg_rep_size_err');
	var rep_size = form_template.firstElementChild.nextElementSibling; // 5 times faster than prev statement
	// var rep_mime = form_template.querySelector('#pg_rep_mime_err');
	var rep_mime = form_template.firstElementChild.nextElementSibling.nextElementSibling; // 3 times faster than prev statement
	form_template.onsubmit = personal_group_reply_submit;
};// call personal_group_reply_submit if form_template is submitted

var rep_text_field = document.getElementById('rep_text_field');
if (rep_text_field) {rep_text_field.onfocus = remove_placeholder;};

var browse_rep_image_btn = document.getElementById('browse_rep_image_btn');//select direct reply's image upload button
if (browse_rep_image_btn) {browse_rep_image_btn.onchange = show_rep_image_name;}


var rep_btns = document.getElementsByClassName('rep');//selects all 'rep' buttons from personal_group_their_chat_buttons (much faster than querySelectorAll)
// var rep_btns = document.querySelectorAll('button.rep');//selects all 'rep' buttons from personal_group_their_chat_buttons
for (var i=0, len=rep_btns.length; i < len; i++) rep_btns[i].onclick = toggle_rep;


var is_reply = false;
var valid_rep_img = false;

var rep_tt = null;
var rep_bid = null;
var rep_idx = null;
var rep_tid = null;
var rep_sk = null;


function remove_placeholder(e) {
	this.placeholder = '';
}

function show_rep_image_name(e) { 
	// if opera mini, do nothing
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.target.files) return;
	var filename = e.target.value.replace(/^.*[\\\/]/, '').slice(0,20);

	var rep_filename = document.getElementById('rep_filename');
	var camera_icon = document.getElementById('rep_cam');
	var ok_btn = document.getElementById('rep_subform');

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
							rep_size.style.display = 'none';
							rep_mime.style.display = 'none';
							ok_btn.disabled = false;
							break;
						case "47494638":
							valid_rep_img = 'gif';
							rep_size.style.display = 'none';
							rep_mime.style.display = 'none';
							ok_btn.disabled = false;
							break;
						case "ffd8ffe0":
						case "ffd8ffe1":
						case "ffd8ffe2":
						case "ffd8ffe3":
						case "ffd8ffe8":
						case "ffd8ffdb":
							valid_rep_img = 'jpeg';
							rep_size.style.display = 'none';
							rep_mime.style.display = 'none';
							ok_btn.disabled = false;
							break;
						default:
							valid_rep_img = null;
							rep_size.style.display = 'none';
							rep_mime.style.display = 'block';
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
		rep_mime.style.display = 'none';
		rep_size.style.display = 'block';
	}

}

 
function personal_group_reply_submit(e) {
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || detect_android_ver() < 4.1) return;
	// This can preventDefault only if image is attached, otherwise do nothing
	if (valid_rep_img) {
		e.preventDefault();

		var image_file = browse_rep_image_btn.files[0];//document.getElementById('browse_rep_image_btn').files[0];
		var rep_text = document.getElementById('rep_text_field').value;
		var target_action = form_template.action;
		
		rep_tt = document.getElementById('rep_tt').value;
		rep_bid = document.getElementById('rep_bid').value;
		rep_idx = document.getElementById('rep_idx').value;
		rep_tid = document.getElementById('rep_tid').value;
		rep_sk = document.getElementById('rep_sk').value;      
		
		personal_group_preloader('create');

		// prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
		prep_image(image_file,rep_text, image_file.name, target_action, 'pg_reply','rep_image', 'rep_reply', '/1-on-1/',null ,process_ajax);
	} else {
		if (valid_rep_img == null) {
			e.preventDefault();
			return;
		} else {
			return;
		}
	}
}

// var milliseconds1 = Date.now();
//       for (var i=0,len=50000;i<len;i++){
//       }
//       var milliseconds2 = Date.now();
//       console.log('time-diff of method2:');
//       console.log(milliseconds2-milliseconds1);


// turns "direct reply" on and off in JS supported devices
function toggle_rep(e) {
	// error-handling cases
	if (!form_template || Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || detect_android_ver() < 4.1) return;
	
	// prevent form submission
	e.preventDefault();
	
	var parent = this.form;

	var payload = parent.firstElementChild.nextElementSibling.value.split(':');
	var tt = payload[4];
	var bid = payload[0];
	var idx = payload[2];

	// first check if reply form was already added under reply button
	var to_remove = parent.nextElementSibling;//supported

	if (to_remove == null) {

			// remove unneeded input fields
			empty_input_fields();


			// moving ghost form into position
			parent.insertAdjacentElement('afterend', form_template);

			// creating and appending desired input fields in form_template
			populate_input_fields(tt, bid, idx);

			// make the form visible
			form_template.style.display = 'inline';

	} else {

	 if (to_remove != null && to_remove.id == 'form_template') {

			// toggle form visibility
			if ( form_template.style.display == 'inline' ) { 
				form_template.style.display = 'none';
				
				// remove unneeded input fields
				empty_input_fields();
			}
			else {

				// remove unneeded input fields
				empty_input_fields();

				// moving ghost form into position
				parent.insertAdjacentElement('afterend', form_template);
				
				// creating and appending desired input fields in form_template
				populate_input_fields(tt, bid, idx);

				// make the form visible
				form_template.style.display = 'inline';
			}

			

	} else {

			// remove unneeded input fields
			empty_input_fields();

			// moving ghost form into position
			parent.insertAdjacentElement('afterend', form_template);

			// creating and appending desired input fields in form_template
			populate_input_fields(tt, bid, idx);

			// make the form visible
			form_template.style.display = 'inline';

	}

	}
};


// inserting relevant values in input fields of form_template (event dispatcher is commented)
function populate_input_fields(tt, bid, idx) {
	
		var field1 = document.getElementById('rep_tt');
		field1.value = tt;
		// var e1 = new UIEvent('change', {
		//     'view': window,
		//     'bubbles': true,
		//     'cancelable': true
		// });
		// field1.dispatchEvent(e1);

		var field2 = document.getElementById('rep_bid');
		field2.value = bid;
		//  var e2 = new UIEvent('change', {
		//     'view': window,
		//     'bubbles': true,
		//     'cancelable': true
		// });
		// field2.dispatchEvent(e2);

		var field3 = document.getElementById('rep_idx');
		field3.value = idx;
		//  var e3 = new UIEvent('change', {
		//     'view': window,
		//     'bubbles': true,
		//     'cancelable': true
		// });
		// field3.dispatchEvent(e3);

}



// empties relevant fields of universal form #form_template (event dispatcher is commented)
function empty_input_fields() {

		var field1 = document.getElementById('rep_tt');
		field1.value='';
		// var event1 = new UIEvent('change', {
		//     'view': window,
		//     'bubbles': true,
		//     'cancelable': true
		// });
		// field1.dispatchEvent(event1);

		var field2 = document.getElementById('rep_bid');
		field2.value='';
		// var event2 = new UIEvent('change', {
		//     'view': window,
		//     'bubbles': true,
		//     'cancelable': true
		// });
		// field2.dispatchEvent(event2);

		var field3 = document.getElementById('rep_idx');
		field3.value='';
		// var event3 = new UIEvent('change', {
		//     'view': window,
		//     'bubbles': true,
		//     'cancelable': true
		// });
		// field3.dispatchEvent(event3);

}

////////////////////////////////////////////////

// var notif_screen_show_all_init_btn = document.getElementById('notif_screen_show_all_init_btn');
// if (notif_screen_show_all_init_btn) {notif_screen_show_all_init_btn.onclick = currentPermNavbar;}

var all_notif_btns = document.getElementsByClassName('all_notif_btn');
if (all_notif_btns) {
  for (var i=0, len=all_notif_btns.length; i < len; i++) all_notif_btns[i].onclick = currentPermNavbar;
}

function currentPermNavbar(e){
  // handles the notification button in the navbar

  var tid = e.currentTarget.value

  if (tid) {
	e.preventDefault();
	renderNotificationOptions(tid)
  } else {
	// do something else - 'tid' not found
	return;
  }
  
}




var allow_notif_btns = document.getElementsByClassName('allow_notif_btn');
if (allow_notif_btns) {
	for (var i=0, len=allow_notif_btns.length; i < len; i++) allow_notif_btns[i].onclick = currentPermAllowBtn;
}

// function currentPermAllowBtn(e){
//   // handles the 'allow notification' button that shows up in 1on1 chat
//   e.preventDefault();

//   var target_id = document.getElementById("notif_tid");
//   var show_allow_only = document.getElementById("notif_show_allow_only");
//   alert(target_id.value);
//   alert(show_allow_only.value);
//   var tid = target_id.value
//   var show_allow_only_value = show_allow_only.value

//   if (tid) {
//     renderNotificationOptions(tid, show_allow_only_value)
//   } else {
//     // do something else - 'tid' not found
//   }

// }

function currentPermAllowBtn(e){
	// handles the 'allow notification' button that shows up in 1on1 chat

	var target_id = document.getElementById("notif_tid");
	var show_allow_only = document.getElementById("notif_show_allow_only");
	var tid = target_id.value
	var show_allow_only_value = show_allow_only.value

	if (tid) {
		e.preventDefault();
		renderNotificationOptions(tid, show_allow_only_value)
	} else {
		// do something else - 'tid' not found
		return;
	}
}

function renderNotificationOptions(target_id, show_allow_only_value) {

	var form_data = new FormData();
	form_data.append("tid",target_id);
	if (show_allow_only_value) {
		form_data.append("show_allow_only",show_allow_only_value);
	}
	/////////////////////////////
	var NotificationIsSupported = !!(window.Notification /* W3C Specification */ || window.webkitNotifications /* old WebKit Browsers */ || navigator.mozNotification /* Firefox for Android and Firefox OS */)
	if ( (!NotificationIsSupported) || (!('serviceWorker' in navigator)) || (!('PushManager' in window))) {
		// handles the case where the browser supports JS but not web notifications (e.g. Safari)
		form_data.append("browser_incompat",'1')
	} else {
		if (Notification.permission === "granted") {
			form_data.append("notif_perm",'1');
		} else if (Notification.permission === "denied"){
			form_data.append("notif_perm",'3');
		} else {
			form_data.append("notif_perm",'2');
		}
	}
	/////////////////////////////
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/1-on-1/push-notif/settings/');// url gotten from from urls_push_notif.py
	xhr.timeout = 15000; // time in milliseconds, i.e. 15 seconds
	xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	xhr.onload = function () {
		var data = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
		if (this.status == 200) {
			window.location.replace(data.redirect);
		} else {
			// e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
			window.location.replace('/push-notification/subscription/unavailable/');
		}
	};
	xhr.onerror = function () {
		// onerror fires when there is a failure on the network level
		window.location.replace('/push-notification/subscription/unavailable/');
	};
	xhr.ontimeout = function (e) {
		// XMLHttpRequest timed out
		window.location.replace('/push-notification/subscription/unavailable/');
	};
	xhr.onprogress = function () {
		// if needed
	};
	xhr.send(form_data);

}


// function currentPermission(e){

//   e.preventDefault();
//   var target_show_all_id = document.getElementById("notif_show_all_tid");
//   var target_id = document.getElementById("notif_tid");
//   if (target_id) {
//     var show_allow_only = document.getElementById("notif_show_allow_only");
//     var tid = target_id;
//   } else {
//     var tid = target_show_all_id;
//   }
//   var form_data = new FormData();
//   form_data.append("tid",tid.value);
//   if (show_allow_only) {
//     form_data.append("show_allow_only",show_allow_only.value);
//   }
//   if ((!('serviceWorker' in navigator)) || (!('PushManager' in window))) {
//     // handles the case where the browser supports JS but not web notifications (e.g. Safari)
//     form_data.append("browser_incompat",'1')
//   }
//   if (("Notification" in window) && Notification.permission === "granted") {
//     form_data.append("notif_perm",'1');
//   } else if (("Notification" in window) && Notification.permission === "denied"){
//     form_data.append("notif_perm",'3');
//   } else if (("Notification" in window)){
//     form_data.append("notif_perm",'2');
//   } else {
//     form_data.append("browser_incompat",'1');
//   }
//   var xhr = new XMLHttpRequest();
//   xhr.open('POST', '/1-on-1/push-notif/settings/');// url gotten from from urls_push_notif.py
//   xhr.timeout = 15000; // time in milliseconds, i.e. 15 seconds
//   xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
//   xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
//   xhr.onload = function () {
//     var data = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
//     if (this.status == 200) {
//       window.location.replace(data.redirect);
//     } else {
//       // e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level)
//       window.location.replace('/push-notification/subscription/unavailable/');
//     }
//   };
//   xhr.onerror = function () {
//     // onerror fires when there is a failure on the network level
//     window.location.replace('/push-notification/subscription/unavailable/');
//   };
//   xhr.ontimeout = function (e) {
//     // XMLHttpRequest timed out
//     window.location.replace('/push-notification/subscription/unavailable/');
//   };
//   xhr.onprogress = function () {
//     // if needed
//   };
//   xhr.send(form_data);
// }


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
		prep_image(browse_pub_img_btn.files[0],pub_img_caption_field.value, browse_pub_img_btn.files[0].name, e.target.action, 'public_img','image_file', 'caption', '/share/photo/upload/',null,process_ajax);
	} else {
		if (valid_public_img == null) {
			e.preventDefault();
			return;
		} else {
			return;
		}
	}
};


function retrieve_audience(){

	var aud_first = document.getElementById('aud-first');
	var aud_second = document.getElementById('aud-second');
	var aud_third = document.getElementById('aud-third');
	var aud_default = document.getElementById('aud-default');
	if (aud_first.checked || aud_second.checked || aud_third.checked){
		if (aud_first.checked) {
			return aud_first.value;
		} else if (aud_second.checked) {
			return aud_second.value;
		} else if (aud_third.checked) {
			return aud_third.value;
		} else {
			return aud_first.value;
		}
	}
	else {
			return 'p';
	}
}

function retrieve_expiry(){

	var exp_first = document.getElementById('exp-first');
	var exp_second = document.getElementById('exp-second');
	var exp_third = document.getElementById('exp-third');
	var exp_default = document.getElementById('exp-default');
	if (exp_first.checked || exp_second.checked || exp_third.checked ){
		if (exp_first.checked) {
			return exp_first.value;
		} else if (exp_second.checked) {
			return exp_second.value;
		} else if (exp_third.checked) {
			return exp_third.value;
		} else {
			return exp_first.value;
		}
	}
	else {
			return 'i';
	}
}

function retrieve_comments(){

	var com_on = document.getElementById('com-on');
	var com_off = document.getElementById('com-off');
	var com_default = document.getElementById('com-default');
	
	// console.log(com_default.value)
	if (com_on.checked || com_off.checked){
		if (com_on.checked) {
			return com_on.value;
		} else {
			return com_off.value;
		}
	}
	else {
			return '1'
	}
}


/////////////////////////////////////////////////////////
// Uploading Photos in Mehfils (JS functionality)
var is_grp_img = false;
var valid_grp_img = false;
var grp_form = document.getElementById('grp_form');//supported
if (grp_form) {grp_form.onsubmit = grp_form_submit;};
var grp_browse_image_btn = document.getElementById('grp_browse_image_btn');//supported
if (grp_browse_image_btn) {grp_browse_image_btn.onchange = validate_grp_img;};

// var grp_writer_id = -1;
// var grp_wid_input = document.getElementById('grp_wid');
// var atbtns = document.getElementsByClassName('at');
// if (atbtns) {
// 	for (var i=0, len=atbtns.length; i < len; i++) atbtns[i].onclick = grp_at_submit;
// }

// function grp_at_submit(e) {
// 	var vb = e.currentTarget;//at button
// 	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !vb.value || !vb) return;
// 	grp_wid_input.value = vb.value;
// 	grp_writer_id = vb.value;
// 	document.getElementById("grp_subform").click();
// }

function validate_grp_img(e) { 
	// if opera mini, do nothing
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.target.files) return;
	document.getElementById("grp_img_size_err").style.display = 'none';
	document.getElementById("grp_img_mime_err").style.display = 'none';
	if (e.target.files[0].size < 20000001){ // don't allow files bigger than 20000000 Bytes (20 MB), since that is the server-side (nginx) limit as well
		if (window.FileReader && window.Blob){
			is_grp_img = true;
			validate_img_file(e);
		}
	} else {throw_err(e.target,'size','grp_img');};
};

function grp_form_submit(e) {
	if (detect_android_ver() < 4.1) return;
	// This can preventDefault only if image is attached, otherwise do nothing
	if (valid_grp_img) {
		e.preventDefault();
		personal_group_preloader('create');
		var fail_ele = document.getElementById('furl');
		var fail_url = fail_ele.value;
		// prep_image does some asynchronous things, so utilize callback by passing process_ajax() as an argument
		prep_image(grp_browse_image_btn.files[0],grp_text_field.value, grp_browse_image_btn.files[0].name, e.target.action, 'grp_img', 'image', 'text', fail_url,null,process_ajax);
	} else {return;};
};