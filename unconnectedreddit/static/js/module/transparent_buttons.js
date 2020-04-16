// feeder for ''
// Compress via https://jscompress.com/ and press "download"
// Or use http://esprima.org/demo/minify.html in case above gives an error

var fbtns = document.getElementsByClassName('fbtn');
for (var i=0, len=fbtns.length; i < len; i++) fbtns[i].onclick = process_follow;

function process_follow(e){

	var fb = e.currentTarget;//follow_button
	var name = fb.name;
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !fb.value || !name) return;
	e.preventDefault();
	
	var payload = fb.value.split("*");
	var topic = payload[0];
	var obid = payload[1];
	var obj_hash = payload[2];
	var origin = payload[3];
	var target_user_id = payload[4];
	var target_username = payload[5];
	var page_num = payload[6];

	///////////////////////////
	var all_tgt_fbtns = document.getElementsByClassName(target_user_id);

	for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

		all_tgt_fbtns[i].disabled = true;//disable the button so that it can't be double clicked

		var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
		var follow_btn_contents = follow_btn.childNodes;// follow button's divs
		var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
		var label_div = follow_btn_contents[1];// 'FOLLOW' label
		var label = label_div.innerHTML;

		toggle_follow_btn(follow_btn, svg_img, label_div, label);

	}

	///////////////////////////

	// var follow_btn = fb.form.getElementsByTagName("button")[0];
	// var follow_btn_contents = follow_btn.childNodes;// follow button's divs
	// var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
	// var label_div = follow_btn_contents[1];// 'FOLLOW' label
	// var label = label_div.innerHTML;

	// toggle_follow_btn(follow_btn, svg_img, label_div, label);

	if (typeof target_user_id !== 'undefined') {
		var form_data = new FormData();
		form_data.append(name, fb.value);
		var xhr = new XMLHttpRequest();
		
		if (label === 'FOLLOW') {
			xhr.open('POST', '/follow/add/');
		} else if (label === 'UNFOLLOW'){
			xhr.open('POST', '/follow/remove/');
		} else {
			xhr.open('POST', '/follow/add/');
		}
		
		xhr.timeout = 15000; //15 seconds
		xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
  		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

  		// XMLHttpRequest went through - and the server either responded with a 'success' message or a 'failure' one
  		xhr.onload = function () {
  			// fb.disabled = false;
  			if (this.status == 200) {
  				
  				var resp = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
  				
  				if (resp.success) {
  					// process the action
		      		if (resp.message === 'followed') {
						// followed successfully
						for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {
		      				all_tgt_fbtns[i].disabled = false;//enable the button(s)
		      			}
						var prompt_string = 'You followed '.concat(target_username)
						display_and_fade_out(prompt_string,determine_pause_length(prompt_string),'notif');//pass message and pause time
		      		} else if (resp.message === 'unfollowed') {
		      			// unfollowed successfully
		      			for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {
		      				all_tgt_fbtns[i].disabled = false;//enable the button(s)
		      			}
		      			var prompt_string = 'You unfollowed '.concat(target_username)
		      			display_and_fade_out(prompt_string,determine_pause_length(prompt_string),'notif');//pass message and pause time
		      		} else {
		      			// do nothing (since the action is unrecognized as follow or unfollow), reverse the actions visually
		      			
		      			for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

		      				var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
							var follow_btn_contents = follow_btn.childNodes;// follow button's divs
							var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
							var label_div = follow_btn_contents[1];// 'FOLLOW' label
							toggle_follow_btn(follow_btn, svg_img, label_div, 'default');

		      			}
		      		}
  				} else {
  					// e.g. if message.success was False
		      		if (resp.type === 'text') {

		      			for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

		      				all_tgt_fbtns[i].disabled = false;//enable the button

		      				var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
							var follow_btn_contents = follow_btn.childNodes;// follow button's divs
							var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
							var label_div = follow_btn_contents[1];// 'FOLLOW' label
							toggle_follow_btn(follow_btn, svg_img, label_div, 'default');

		      			}
		      			// display disappearing popup with resp.message
						display_and_fade_out(resp.message,determine_pause_length(resp.message),'err');//pass message and pause time

		      		} else if (resp.type === 'redirect') {
		      			// redirect to provided url
		      			// alert(resp);
		      			window.location.replace(resp.message);
		      		} else {
		      			// do nothing and reverse the action visually
		      			for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

		      				all_tgt_fbtns[i].disabled = false;//enable the button

		      				var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
							var follow_btn_contents = follow_btn.childNodes;// follow button's divs
							var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
							var label_div = follow_btn_contents[1];// 'FOLLOW' label
							toggle_follow_btn(follow_btn, svg_img, label_div, 'default');

		      			}
		      		}
  				}

  			} else {
  				// e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level - where there are no error codes)
  				// reverse the action visually
  				for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

      				all_tgt_fbtns[i].disabled = false;//enable the button

      				var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
					var follow_btn_contents = follow_btn.childNodes;// follow button's divs
					var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
					var label_div = follow_btn_contents[1];// 'FOLLOW' label
					toggle_follow_btn(follow_btn, svg_img, label_div, 'default');

      			}
  			}
  		}

  		// when there is a failure on the network level, no response is received (e.g. a denied cross-domain request, or internet off)
  		xhr.onerror = function () {

  			// reverse the action visually
  			for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

  				all_tgt_fbtns[i].disabled = false;//enable the button

  				var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
				var follow_btn_contents = follow_btn.childNodes;// follow button's divs
				var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
				var label_div = follow_btn_contents[1];// 'FOLLOW' label
				toggle_follow_btn(follow_btn, svg_img, label_div, 'default');

  			}
  			var err_msg = 'Kuch kharab ho gaya, dubara try karein';
			display_and_fade_out(err_msg,determine_pause_length(err_msg),'err');//pass message and pause time
  		}

  		xhr.onprogress = function () {
  			// do nothing
  		}

  		// XMLHttpRequest timed out
  		xhr.ontimeout = function (e) {
  			// reverse the action visually
  			for (var i=0, len=all_tgt_fbtns.length; i < len; i++) {

  				all_tgt_fbtns[i].disabled = false;//enable the button

  				var follow_btn = all_tgt_fbtns[i].form.getElementsByTagName("button")[0];
				var follow_btn_contents = follow_btn.childNodes;// follow button's divs
				var svg_img = follow_btn_contents[0].childNodes[0];// the follow svg
				var label_div = follow_btn_contents[1];// 'FOLLOW' label
				toggle_follow_btn(follow_btn, svg_img, label_div, 'default');

  			}
		   	var err_msg = 'Internet slow hai, baad mein try karein';
			display_and_fade_out(err_msg,determine_pause_length(err_msg),'err');//pass message and pause time
  		}

  		xhr.send(form_data);
	
	} else {
		// do nothing
	}

}

function toggle_follow_btn(follow_btn, svg_img, btn_label_div, force_state){

	if (force_state === 'FOLLOW') {
		// it is a 'follow' action
		follow_btn.style.border = '1px solid #a9a9a9';// changing follow button's border color
		svg_img.src = '/static/img/unfollow.svg';// changing the icon
		btn_label_div.style.color = '#a6a6a6'// changing color of 'FOLLOW' label
		btn_label_div.innerHTML = 'UNFOLLOW';// changing 'FOLLOW' label to 'UNFOLLOW'
		return true;// forced to toggle
	
	} else if (force_state === 'UNFOLLOW') {
		// 'follow' action is reversed
		follow_btn.style.border = '1px solid #7f68fd';// changing unfollow button's border color
		svg_img.src = '/static/img/follow.svg';// changing the icon
		btn_label_div.style.color = '#7f68fd'// changing color of 'UNFOLLOW' label
		btn_label_div.innerHTML = 'FOLLOW';// changing 'UNFOLLOW label to 'FOLLOW'
		return true;// forced to state toggle
	
	} else {
		// just toggle the state depending on what the current label is
		var current_state = btn_label_div.innerHTML;

		if (current_state === 'FOLLOW') {
			follow_btn.style.border = '1px solid #a9a9a9';// changing follow button's border color
			svg_img.src = '/static/img/unfollow.svg';// changing the icon
			btn_label_div.style.color = '#a6a6a6'// changing color of 'FOLLOW' label
			btn_label_div.innerHTML = 'UNFOLLOW';// changing 'FOLLOW' label to 'UNFOLLOW'
			return false;

		} else {
			follow_btn.style.border = '1px solid #7f68fd';// changing unfollow button's border color
			svg_img.src = '/static/img/follow.svg';// changing the icon
			btn_label_div.style.color = '#7f68fd'// changing color of 'UNFOLLOW' label
			btn_label_div.innerHTML = 'FOLLOW';// changing 'UNFOLLOW label to 'FOLLOW'
			return false;
		}
		
	}

}

///////////////////////////////////////////////////////////////////////////////////


var sv = false; // self_voting
var vbtns = document.getElementsByClassName('vbtn');
for (var i=0, len=vbtns.length; i < len; i++) vbtns[i].onclick = cast_vote;

// $('.vbtn').click(cast_vote(e)); jQuery

function cast_vote(e) {
	var vb = e.currentTarget;//vote_button
	var name = vb.name;

	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !vb.value || !name) return;
	e.preventDefault();

	vb.disabled = true;//disable the button so that it can't be double clicked
	
	var payload = vb.value.split(":");
	var lid = payload[0]; // link_id
	var ooid = payload[1]; // link_writer_id
	var is_pht = payload[2]; // is_pht == '1' if object is a photo
	var origin = payload[3]; // voting origin

	var ident = document.getElementById("uident");
	if (typeof ident !== 'undefined') {
		if (ident.value === ooid) sv = true;
	}

	if (sv === true) {
		// trying to like own content!
		var err_msg = 'Apni post ko like nahi kar saktey';
		display_and_fade_out(err_msg,determine_pause_length(err_msg),'err');//pass message and pause time
		sv = false;
		vb.disabled = false;

	} else {
		// proceed
		var like_btn = vb.form.getElementsByTagName("button")[0];
		var like_btn_contents = like_btn.childNodes;// like button's divs
		var svg_img = like_btn_contents[0].childNodes[0];// the <3 svg
		var label_div = like_btn_contents[1];// 'LIKE' label
		toggle_like_btn(like_btn, svg_img, label_div);

		if (typeof lid !== 'undefined' && typeof ident !== 'undefined') {
			var form_data = new FormData();
			form_data.append(name, vb.value);
			var xhr = new XMLHttpRequest();
			xhr.open('POST', '/cast_vote/');
			xhr.timeout = 15000; //15 seconds
			xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
	  		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	  		xhr.onload = function () {
	  			vb.disabled = false;
	  			if (this.status == 200) {
			      	var resp = JSON.parse(this.responseText);//supported, because xhr.responseType is text, which is coverted to JSON upon receipt
			      	if (resp.success) {
			      		// process the vote
			      		if (resp.message === 'new') {
							// fresh like
							var forced_to_toggle = toggle_like_btn(like_btn, svg_img, label_div, 'unlike');
							if (!forced_to_toggle) {
								display_and_fade_out('Liked & Saved!',determine_pause_length('Liked & Saved!'),'notif');//pass message and pause time
							}
			      		} else if (resp.message === 'old') {
			      			// reverting prev like
			      			var forced_to_toggle = toggle_like_btn(like_btn, svg_img, label_div, 'like');
			      			if (!forced_to_toggle) {
			      				display_and_fade_out('Removed Like & Save!',determine_pause_length('Removed Like & Save!'),'notif');//pass message and pause time
			      			}
			      		} else {
			      			// do nothing since the vote is unrecognized as like or unlike
			      		}

			      	} else {
			      		// e.g. if message.success was False
			      		if (resp.type === 'text') {
			      			// reverse the vote visually
							toggle_like_btn(like_btn, svg_img, label_div);
			      			// display disappearing popup with resp.message
							display_and_fade_out(resp.message,determine_pause_length(resp.message),'err');//pass message and pause time
							
			      		} else if (resp.type === 'redirect') {
			      			// redirect to provided url
			      			// alert(resp);
			      			window.location.replace(resp.message);
			      		} else {
			      			// do nothing
			      		}
			      	}
			    } else {
			      	// e.g. if status == 404 or 403 or 500 (this is an error at the application level, not network level - where there are no error codes)
			      	var err_msg = 'Kuch ghalat ho gaya, dubara try karein';
			      	// reverse the vote visually
			      	toggle_like_btn(like_btn, svg_img, label_div);
					display_and_fade_out(err_msg,determine_pause_length(err_msg),'err');//pass message and pause time
			  
			    }
	  		};
	  		xhr.onerror = function () {
	  			// onerror fires when there is a failure on the network level, no response is received (e.g. a denied cross-domain request, or internet off)
	  			vb.disabled = false;
	  			// reverse the vote visually
			   	var err_msg = 'Kuch kharab ho gaya, dubara try karein';
				display_and_fade_out(err_msg,determine_pause_length(err_msg),'err');//pass message and pause time
				toggle_like_btn(like_btn, svg_img, label_div);
		  
	  		};
	  		xhr.onprogress = function () {
	  			// do nothing
	  		};
	  		xhr.ontimeout = function (e) {
	  			// XMLHttpRequest timed out
	  			vb.disabled = false;
	  			// reverse the vote visually
			   	var err_msg = 'Internet slow hai, baad mein try karein';
				display_and_fade_out(err_msg,determine_pause_length(err_msg),'err');//pass message and pause time
				toggle_like_btn(like_btn, svg_img, label_div);
		  
	  		};
	  		xhr.send(form_data);

		} else {
			// do nothing
		}
	}	
}

function toggle_like_btn(like_btn, svg_img, btn_label_div, force_state) {
	if (typeof force_state === 'undefined') {
		if (btn_label_div.innerHTML === 'LIKE') {
			// it is a 'like' action
			like_btn.style.border = '1px solid #d3d3d3';// changing like button's border color
			svg_img.src = '/static/img/unlike.svg';// changing <3 icon to a gray icon
			btn_label_div.style.color = '#808080'// changing color of 'LIKE' label
			btn_label_div.innerHTML = 'UNLIKE';// changing 'LIKE' label to 'UNLIKE'
			return true;// state toggled
		} else if (btn_label_div.innerHTML === 'UNLIKE') {
			// like is reversed
			like_btn.style.border = '1px solid #f30051';// changing like button's border color
			svg_img.src = '/static/img/like.svg';// changing the gray <3 icon to the pink one
			btn_label_div.style.color = '#f30051'// changing color of 'UNLIKE' label
			btn_label_div.innerHTML = 'LIKE';// changing 'UNLIKE' label to 'LIKE'
			return true;// state toggled
		} else {
			// consider it a like
			like_btn.style.border = '1px solid #d3d3d3';// changing like button's border color
			svg_img.src = '/static/img/unlike.svg';// changing <3 icon to a gray icon
			btn_label_div.style.color = '#808080'// changing color of 'LIKE' label
			btn_label_div.innerHTML = 'UNLIKE';// changing 'LIKE' label to 'UNLIKE'
			return true;// state toggled
		}
	} else if (force_state === 'like') {
		if (btn_label_div.innerHTML === 'LIKE') {
			// button is already at the required state, do nothing
			return false;// did not have to be forced
		} else {
			// force button to assume the 'like' form
			like_btn.style.border = '1px solid #f30051';// changing like button's border color
			svg_img.src = '/static/img/like.svg';// changing the gray <3 icon to the pink one
			btn_label_div.style.color = '#f30051'// changing color of 'UNLIKE' label
			btn_label_div.innerHTML = 'LIKE';// changing 'UNLIKE' label to 'LIKE'
			return true;// had to be forced
		}
		
	} else if (force_state === 'unlike') {
		if (btn_label_div.innerHTML === 'UNLIKE') {
			// button is already at the required state, do nothing
			return false;// did not have to be forced
		} else {
			// force button to assume the 'unlike' form
			like_btn.style.border = '1px solid #d3d3d3';// changing like button's border color
			svg_img.src = '/static/img/unlike.svg';// changing <3 icon to a gray icon
			btn_label_div.style.color = '#808080'// changing color of 'LIKE' label
			btn_label_div.innerHTML = 'UNLIKE';// changing 'LIKE' label to 'UNLIKE'
			return true;// had to be forced
		}
	} else {
		// do nothing
	}
}

// function update_btn_content(value,score_div,label_div,pts_btn,content_color,label) {
// 	var old_score = score_div.innerHTML;
// 	if (value === '1') {
// 		// it is an upvote
// 		if (old_score === '999+' || old_score == '-999') {
// 			// can't change score
// 			// return ['999+','999+'];
// 		} else {
// 			// can change score
// 			old_score = parseInt(old_score,10);
// 			var new_score = old_score + 1//convert innerHtml to int before adding 1 to it
// 			score_div.innerHTML = new_score;
// 			if (new_score === 1 && label === 'POINTS') {
// 				// change language
// 				label_div.innerHTML = 'POINT';
// 			} else if (new_score !==1 && label === 'POINT') {
// 				// change language
// 				label_div.innerHTML = 'POINTS';
// 			} else {
// 				// do nothing
// 				// console.log("not changing plurality");
// 			}
// 			if (new_score < 0 && content_color != 'rgb(255, 99, 71)') {
// 				// turn label into a reddish color (only RGB values supported)
// 				pts_btn.style.color = 'rgb(255, 99, 71)';
// 			} else if (new_score > -1 && content_color != 'rgb(24, 180, 136)') {
// 				// turn label into a greenish color (only RGB values supported)
// 				pts_btn.style.color = 'rgb(24, 180, 136)';
// 			} else {
// 				// do nothing
// 				// console.log("not changing color");
// 			}
// 			// return [old_score, new_score];
// 		}
// 	} else if (value === '0') {
// 		// it is a downvote
// 		if (old_score === '-999' || old_score === '999+') {
// 			// can't change score
// 			// can't change score
// 		} else {
// 			// can change score
// 			old_score = parseInt(old_score,10);
// 			var new_score = old_score - 1//convert innerHtml to int before subtracting 1 from it
// 			score_div.innerHTML = new_score;
// 			if (new_score === 1 && label === 'POINTS') {
// 				// change language
// 				label_div.innerHTML = 'POINT';
// 			} else if (new_score !==1 && label === 'POINT') {
// 				// change language
// 				label_div.innerHTML = 'POINTS';
// 			} else {
// 				// do nothing
// 				// console.log("not changing plurality");
// 			}
// 			if (new_score < 0 && content_color != 'rgb(255, 99, 71)') {
// 				// turn label into a reddish color (only RGB values supported)
// 				pts_btn.style.color = 'rgb(255, 99, 71)';
// 			} else if (new_score > -1 && content_color != 'rgb(24, 180, 136)') {
// 				// turn label into a greenish color (only RGB values supported)
// 				pts_btn.style.color = 'rgb(24, 180, 136)';
// 			} else {
// 				// do nothing
// 				// console.log("not changing color");
// 			}
// 			// return [old_score, new_score];
// 		}
// 	} else {
// 		// any other value is not to be processed. Do nothing
// 		// return [null, null];
// 	}

// }

function determine_pause_length(string) {
	// we assume that longer the string, longer it takes to read (exponentially so, not linearly)

	var length = string.length;
	// determine ttl of popup

	var base_length = 9;
	var base_ttr = 350; // ttr is time to read
	var max_ttr = 6000;

	if (length < base_length) {
		return base_ttr;
	} else {
		var bigness_ratio = (length-base_length) / (length+base_length); // goes to 0 for strings close to base_length, and goes to 1 for very large strings

		// scaling reading_time dilation between [1 - 1.5] interval
		var scale_factor = 1+(0.5*bigness_ratio); // scale up base_ttr according to this

		var determined_ttr = Math.round(Math.pow(base_ttr, scale_factor));// base_ttr raised to the power scale_factor

		if (determined_ttr > max_ttr) {
			return max_ttr;
		} else {
			return determined_ttr; // returns base_ttr^scale_factor
		}
	}
}

///////////////////////////////////////////////////////////////////////////////////

// var share_btns = document.getElementsByClassName('share');
// for (var i=0, len=share_btns.length; i < len; i++) share_btns[i].onclick = share_modal;


// function share_modal(e) {

// 	var pop_up = document.getElementById("share_popup");
// 	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.currentTarget.value || !pop_up) return;
// 	e.preventDefault();

// 	var overlay = document.createElement('div');
//     overlay.id = "personal_group_overlay";
//     overlay.className = 'ovl';//
//     overlay.style.background = '#000000';
//     overlay.style.opacity = '0.5';

//     document.body.appendChild(overlay);
// 	pop_up.style.display = 'block';

// }

///////////////////////////////////////////////////////////////////////////////////

var report_btns = document.getElementsByClassName('report');
for (var i=0, len=report_btns.length; i < len; i++) report_btns[i].onclick = report_modal;

function report_modal(e) {

	var pop_up = document.getElementById("report_popup");
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.currentTarget.value || !pop_up) return;
	e.preventDefault();

	var payload = e.currentTarget.value;
	var payload_type = payload.substring(0, 2);

	if (payload_type === 'tx' || payload_type === 'im' || payload_type === 'pf') {

		if (payload_type === 'tx') {
			var ob_tp = 'tx';
			var type_of_content = document.getElementById("type_txt");

			var payload_array = payload.split("#",8);// one more than python's split (i.e. in python, we would have split by '7')
			
			var content_topic = document.getElementById("tp"+payload_array[2]);
			var report_content = document.getElementById("report_txt");
			report_content.innerHTML = '"'+payload_array[7].substring(0, 40)+' ..."'; // description
			var report_user = document.getElementById("submitter");
			report_user.innerHTML = payload_array[3]; // owner_username
			var report_label = document.getElementById("report_label");
			report_label.innerHTML = 'REPORT<br>TEXT';
			var block_label = document.getElementById("block_label");
			block_label.innerHTML = 'BLOCK<br>USER';
			var target_id = payload_array[4];// owner_id

		} else if (payload_type === 'pf') {
			
			var ob_tp = 'pf';
			var type_of_content = document.getElementById("type_pf");

			var payload_array = payload.split("#",5);// one more than python's split (i.e. in python, we would have split by '7')

			var report_content = document.getElementById("report_pf");
			report_content.src = payload_array[4]; // user's display_pic
			var report_user = document.getElementById("user_profile");
			report_user.innerHTML = payload_array[3]; // username
			var report_label = document.getElementById("report_label");
			report_label.innerHTML = 'REPORT<br>USER';
			var block_label = document.getElementById("block_label");
			block_label.innerHTML = 'BLOCK<br>USER';
			var target_id = payload_array[2];// owner_id

		} else {
			
			var ob_tp = 'img';
			var type_of_content = document.getElementById("type_img");

			var payload_array = payload.split("#",8);// one more than python's split (i.e. in python, we would have split by '7')

			var report_content = document.getElementById("report_img");
			report_content.src = payload_array[5]; // photo_url
			var report_user = document.getElementById("uploader");
			report_user.innerHTML = payload_array[3]; // owner_username
			var report_label = document.getElementById("report_label");
			report_label.innerHTML = 'REPORT<br>PHOTO';
			var block_label = document.getElementById("block_label");
			block_label.innerHTML = 'BLOCK<br>USER';
			var target_id = payload_array[4];// owner_id

		}
		var own_id = document.getElementById("uident").value;// ensure this is always present, or the function will fail

		var overlay = document.createElement('div');
	    overlay.id = "personal_group_overlay";
	    overlay.className = 'ovl';//
	    overlay.style.background = '#000000';
	    overlay.style.opacity = '0.5';

	    if (target_id === own_id) {
	    	// trying to report self or self-item
	    	var own_report = document.getElementById('report_own_item');
			document.body.appendChild(overlay);
			type_of_content.style.display = 'block';
			own_report.style.display = 'block';
			pop_up.style.display = 'block';
			document.getElementById("report_popup_x").onclick = function(){
				if (ob_tp === 'tx') {
					report_content.innerHTML = '';
				} else if (ob_tp == 'pf') {
					report_content.src = '';
				} else {
					report_content.src = '';
				}
				// report_content.src = ''; //OR report_content.innerHTML = ''
				report_user.innerHTML = '';
				own_report.style.display = 'none';
				pop_up.style.display = 'none';
				type_of_content.style.display = 'none';
				overlay.parentNode.removeChild(overlay);
			}
	    } else {
	    	// legit blocking effort
	    	var report_button = document.getElementById('report_btn');
			var block_button = document.getElementById('block_btn');
			document.body.appendChild(overlay);
			pop_up.style.display = 'block';
			type_of_content.style.display = 'block';
			report_button.style.display = 'block';
			block_button.style.display = 'block';

			if (payload_type === 'tx' || payload_type === 'im') {
				// 'tx' and 'im' have similar payloads ('pf' is different, and is handled in 'else')
				var obj_type = document.getElementById('r_tp');
				obj_type.value = ob_tp;// type of object ('tx' or 'img')
				var report_origin = document.getElementById('r_org');
				report_origin.value = payload_array[1]; // origin
				var report_obid = document.getElementById('r_obid');
				report_obid.value = payload_array[2]; // obj_id
				var report_owneruname = document.getElementById('r_oun');
				report_owneruname.value = payload_array[3]; // owner_username
				var report_ownerid = document.getElementById('r_ooid');
				report_ownerid.value = payload_array[4]; // obj_owner_id
				var report_thumburl = document.getElementById('r_url');
				report_thumburl.value = payload_array[5]; // photo_url or avatar_url (depending on content type)
				var report_linkid = document.getElementById('r_lid');
				report_linkid.value = payload_array[6]; // link_id (if home-hash exists)
				var report_caption = document.getElementById('r_cap');
				report_caption.value = payload_array[7]; // caption

				var block_targetusername = document.getElementById('b_tun');
				block_targetusername.value = payload_array[3]; // target username
				var block_origin = document.getElementById('b_org');
				block_origin.value = payload_array[1]; // origin
				var block_linkid = document.getElementById('b_lid');
				block_linkid.value = payload_array[6]; // link_id (if home-hash exists)
				var block_obid = document.getElementById('b_obid');
				block_obid.value = payload_array[2]; // obj_id
				var block_targetid = document.getElementById('b_tid');
				block_targetid.value = "7f"+parseInt(payload_array[4],10).toString(16)+":a"; // target_id to be blocked (converted to hex, and some 'chaff' added)

				if (content_topic && content_topic.value) {
					var block_topic = document.getElementById('b_top');
					var report_topic = document.getElementById('r_top');
					report_topic.value = content_topic.value;
					block_topic.value = content_topic.value;
				}

			} else {
				// handling type 'pf'
				var obj_type = document.getElementById('r_tp');
				obj_type.value = ob_tp; // type of object ('tx' or 'img')
				var report_origin = document.getElementById('r_org');
				report_origin.value = payload_array[1]; // origin
				var report_obid = document.getElementById('r_obid');
				report_obid.value = payload_array[2]; // obj_id
				var report_owneruname = document.getElementById('r_oun');
				report_owneruname.value = payload_array[3]; // owner_username
				var report_ownerid = document.getElementById('r_ooid');
				report_ownerid.value = payload_array[2]; // obj_owner_id
				var report_thumburl = document.getElementById('r_url');
				report_thumburl.value = payload_array[4]; // photo_url or avatar_url (depending on content type)
				var report_linkid = document.getElementById('r_lid');
				report_linkid.value = ''; // link_id (if home-hash exists)
				var report_caption = document.getElementById('r_cap');
				report_caption.value = ''; // caption

				var block_targetusername = document.getElementById('b_tun');
				block_targetusername.value = payload_array[3]; // target username
				var block_origin = document.getElementById('b_org');
				block_origin.value = payload_array[1]; // origin
				var block_linkid = document.getElementById('b_lid');
				block_linkid.value = ''; // link_id (if home-hash exists)
				var block_obid = document.getElementById('b_obid');
				block_obid.value = payload_array[2]; // obj_id
				var block_targetid = document.getElementById('b_tid');
				block_targetid.value = "7f"+parseInt(payload_array[2],10).toString(16)+":a"; // target_id to be blocked (converted to hex, and some 'chaff' added)

			}
			
			document.getElementById("report_popup_x").onclick = function(){
				if (ob_tp === 'tx') {
					report_content.innerHTML = '';
				} else {
					report_content.src = '';
				}
				report_user.innerHTML = '';
				report_label.innerHTML = '';
				block_label.innerHTML = '';
				pop_up.style.display = 'none';
				type_of_content.style.display = 'none';
				report_button.style.display = 'none';
				block_button.style.display = 'none';
				overlay.parentNode.removeChild(overlay);
				
				obj_type.value = '';
				report_origin.value = '';
				report_caption.value = '';
				report_obid.value = '';
				report_owneruname.value = '';
				report_thumburl.value = '';
				report_linkid.value = '';
				report_ownerid.value = '';
				if (report_topic && report_topic.value) {
					report_topic.value = '';
				}

				block_targetid.value = '';
				block_targetusername.value = '';
				if (block_topic && block_topic.value) {
					block_topic.value = '';
				}
			};
	    }

	} else {
		// this shouldn't be allowed
		return;
	}

}

var link_btns = document.getElementsByClassName('link');
for (var i=0, len=link_btns.length; i < len; i++) link_btns[i].onclick = copy_url;


function copy_url(e) {// this is iOS friendly
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.currentTarget.value) return;
 	e.preventDefault();
 	var target_url = 'https://damadam.pk/content/'+e.currentTarget.value+'/g/';
 	var dummy_element = document.createElement('textarea');// Create a dummy textarea to copy the url inside it
 	dummy_element.setAttribute('readonly', true);// Set to readonly
    dummy_element.setAttribute('contenteditable', true);// Set to contenteditable
    dummy_element.style.position = 'fixed'; // prevent scroll from jumping to the bottom when focus is set.
    dummy_element.value = target_url;
 	document.body.appendChild(dummy_element);// Add it to the document
 	// dummy_element.focus();
 	dummy_element.select();// Select it
 	const range = document.createRange();
    range.selectNodeContents(dummy_element);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    dummy_element.setSelectionRange(0, dummy_element.value.length);
 	document.execCommand("copy");// Copy its contents
 	document.body.removeChild(dummy_element);
 	// now display the copied link
 	display_and_fade_out('Link copied',determine_pause_length('Link copied'),'notif');//pass message and pause time
}

function display_and_fade_out(copy,pause,notif_type) {
	if (notif_type === 'err') {
		var prompt = document.getElementById("quick_err_prompt");
	 	var text = document.getElementById("quick_err_text");
	} else {
		var prompt = document.getElementById("quick_prompt");
	 	var text = document.getElementById("quick_text");
	}
 	if (text) text.innerHTML = copy;
 	if (prompt) {
 		var style = prompt.style;
 		style.display = 'block';
		style.opacity = 1;
	}
	// uses a javascript IIFE function expression that recursively calls itself after 30 ms
	if (text && prompt) setTimeout(function(){ (function fade(){(style.opacity-=.1)<0?(style.display="none"):setTimeout(fade,30)})(); }, pause);//fades out
}


function get_cookie(name) {
  if (!name) { return null; }
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length >= 2) return parts.pop().split(";").shift();
}


// previousElementSibling polyfill for Internet Explorer 9+ and Safari
// Source: https://github.com/jserz/js_piece/blob/master/DOM/NonDocumentTypeChildNode/previousElementSibling/previousElementSibling.md
(function (arr) {
  arr.forEach(function (item) {
    if (item.hasOwnProperty('previousElementSibling')) {
      return;
    }
    Object.defineProperty(item, 'previousElementSibling', {
      configurable: true,
      enumerable: true,
      get: function () {
        var el = this;
        while (el = el.previousSibling) {
          if (el.nodeType === 1) {
            return el;
          }
        }
        return null;
      },
      set: undefined
    });
  });
})([Element.prototype, CharacterData.prototype]);



// lastElementChild polyfill for IE8, IE9 and Safari
// Overwrites native 'lastElementChild' prototype.
// Adds Document & DocumentFragment support for IE9 & Safari.
// Returns array instead of HTMLCollection.
;(function(constructor) {
    if (constructor &&
        constructor.prototype &&
        constructor.prototype.lastElementChild == null) {
        Object.defineProperty(constructor.prototype, 'lastElementChild', {
            get: function() {
                var node, nodes = this.childNodes, i = nodes.length - 1;
                while (node = nodes[i--]) {
                    if (node.nodeType === 1) {
                        return node;
                    }
                }
                return null;
            }
        });
    }
})(window.Node || window.Element);