// 1) "hides" the bottom fixed navbar when a text-field is focused
// 2) opens a JS modal that shows 'more' options
///////////////////////////////////////////////////////////////////////////////////

// opening 'more' modal
document.getElementById("more_btn").addEventListener("click", function(e){
  
	var pop_up = document.getElementById("more_popup");
	if (Object.prototype.toString.call(window.operamini) === "[object OperaMini]" || !e.currentTarget.value || !pop_up) return;
	e.preventDefault();

	// display an overlay
	var overlay = document.createElement('div');
    overlay.id = "personal_group_overlay";
    overlay.className = 'ovl';//
    overlay.style.background = '#000000';
    overlay.style.opacity = '0.5';

    // display the modal
    document.body.appendChild(overlay);
	pop_up.style.display = 'block';

	// highlight the 'more' button in the bottom navbar
	var more_btn = document.getElementById("more_btn");
	var more_label = document.getElementById("more_label");
	more_btn.style.backgroundColor = '#00bfa5';
	more_label.style.fontWeight = '600';

}); 

// closing 'more' modal
document.getElementById("more_popup_x").addEventListener("click", function(){

	// hide the modal
	var pop_up = document.getElementById("more_popup");
	pop_up.style.display = 'none';

	// remove the overlay
	var overlay = document.getElementById("personal_group_overlay");
	overlay.parentNode.removeChild(overlay);

	// remove the highlight on the 'more' button in the bottom navbar
	var more_btn = document.getElementById("more_btn");
	var more_label = document.getElementById("more_label");
	more_btn.style.backgroundColor = '#fff';
	more_label.style.fontWeight = '500';
});

///////////////////////////////////////////////////////////////////////////////////

var input_btns = document.getElementsByClassName('inp');// selecting all textareas or inputs for processing (e.g. making fixed bottom menu 'absolute')
for (var i=0, len=input_btns.length; i < len; i++) {
	input_btns[i].onfocus = () => {
		var bottom_nav = document.getElementById("bottom_nav");
		bottom_nav.classList.remove('show-it');
      	bottom_nav.classList.add('hide-it');
	}
	input_btns[i].onblur = () => {
		var bottom_nav = document.getElementById("bottom_nav");
		bottom_nav.classList.remove('hide-it');
      	bottom_nav.classList.add('show-it');
	}
}
