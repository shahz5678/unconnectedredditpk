function showFilename() { 
	var x = document.getElementById('browse_image_btn').value;
	x = x.replace(/^.*[\\\/]/, '')
	document.getElementById('filename').innerHTML = x;
};