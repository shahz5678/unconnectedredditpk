// "hides" the fixed navbar(s) when a text-field is focused

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