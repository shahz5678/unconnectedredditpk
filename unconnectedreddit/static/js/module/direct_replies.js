var max_home_reply_size = 350;

var direct_reply_template = document.getElementById('direct_reply_template');
if (direct_reply_template) {direct_reply_template.onsubmit = validate_direct_reply;};

var dir_rep_btns = document.getElementsByClassName('dir_rep');
for (var i=0, len=dir_rep_btns.length; i < len; i++) dir_rep_btns[i].onclick = toggle_direct_reply_box;

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

function stringIsEmpty(value) {
	// returns true if value is null, undefined (etc) or blank (ie contains only blank spaces)
    return value ? value.trim().length == 0 : true;

}

function reset_err_msgs() {

	var empty_err = document.getElementById('dir_rep_empty');
	var max_err = document.getElementById('dir_rep_max_len_err');
	var err_detail = document.getElementById('dir_rep_chars');

	empty_err.style.display = 'none';
	max_err.style.display = 'none';
	err_detail.innerHTML = '';

}

function validate_direct_reply(e) {

	reset_err_msgs();

	var dir_rep = document.getElementById('dir_rep_body');
	if (stringIsEmpty(dir_rep.value)) {
		// prevent form submission
		e.preventDefault();

		// display error
		var empty_err = document.getElementById('dir_rep_empty');
		
		empty_err.style.display = 'block';
	} else if (dir_rep.value.length > max_home_reply_size) {
		// prevent form submission
		e.preventDefault();

		// populate error detail
		var err_detail = document.getElementById('dir_rep_chars');
		err_detail.innerHTML = dir_rep.value.length;

		// display error
		var max_err = document.getElementById('dir_rep_max_len_err');
		max_err.style.display = 'block';
	}
}


// toggles "direct reply box" (home and reply pages) 'on' and 'off' in JS supported devices
function toggle_direct_reply_box(e) {

// error-handling cases
if (!direct_reply_template || Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || detect_android_ver() < 4.1) return;

// prevent form submission
e.preventDefault();

var parent = this.form;
reset_err_msgs();
var payload = parent.elements['dr_pl'].value.split(':');

var origin = payload[0];
var obtp = payload[1];
var poid = payload[2];
var obid = payload[3];
var tuid = payload[4];
var target_obj_text = payload[5];

// the spot where the 'reply' text box is to be appended
var append_spot = document.getElementById('disc_btns'+obid);

// to check if reply form was already added under reply button
var to_remove = append_spot.nextElementSibling;//supported

if (to_remove == null) {

	// appending form and making it visible!
	empty_input_value();
	append_spot.insertAdjacentElement('afterend', direct_reply_template);
	populate_input_values(poid, obid, tuid, obtp);
	direct_reply_template.style.display = 'block';


} else {

	if (to_remove != null && to_remove.id === 'direct_reply_template') {

		// toggle form visibility
		if ( direct_reply_template.style.display === 'block' ) {
			direct_reply_template.style.display = 'none';
			empty_input_value();
			
		} else {

			// appending form and making it visible!
			empty_input_value();
			append_spot.insertAdjacentElement('afterend', direct_reply_template);
			populate_input_values(poid, obid, tuid, obtp);
			direct_reply_template.style.display = 'block';

		}

	} else {

		// appending form and making it visible!
		empty_input_value();
		append_spot.insertAdjacentElement('afterend', direct_reply_template);
		populate_input_values(poid, obid, tuid, obtp);
		direct_reply_template.style.display = 'block';

	}

}

}

function empty_input_value() {

	document.getElementById("drep_poid").value = '';
	document.getElementById("drep_obid").value = '';
	document.getElementById("drep_tuid").value = '';
	document.getElementById("drep_obtp").value = '';

}

// populating input field values required in direct reply submission
function populate_input_values(poid, obid, tuid, obtp) {

	var field1 = document.getElementById('drep_poid');
	var field2 = document.getElementById('drep_obid');
	var field3 = document.getElementById('drep_tuid');
	var field4 = document.getElementById('drep_obtp');

	field1.value = poid;
	field2.value = obid;
	field3.value = tuid;
	field4.value = obtp;
}