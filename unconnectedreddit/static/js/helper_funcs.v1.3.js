var valid_img=!1,max_img_width=400,wranges=[max_img_width,Math.round(.8*max_img_width),Math.round(.6*max_img_width),Math.round(.4*max_img_width),Math.round(.2*max_img_width)],pg_form=document.getElementById("personal_group_form");pg_form&&(pg_form.onsubmit=personal_group_submit);var browse_image_btn=document.getElementById("browse_image_btn");function detect_android_ver(){var e=navigator.userAgent;return e.indexOf("Android")>=0?parseFloat(e.slice(e.indexOf("Android")+8)):100}function personal_group_preloader(e){switch(e){case"create":(i=document.createElement("div")).id="personal_group_overlay",i.className="ovl",(a=document.createElement("div")).id="personal_group_preloader",a.className="outer_ldr";var t=document.createElement("div");t.className="ldr ma",t.innerHTML="<hr><hr><hr><hr>",(r=document.createElement("div")).id="preloader_message",r.className="cap sp cs cgy mbl",r.innerHTML="- resizing foto -",document.body.appendChild(i),document.body.appendChild(a),a.insertAdjacentElement("afterbegin",t),a.insertAdjacentElement("afterbegin",r),document.body.style.overflow="hidden";break;case"update":(r=document.getElementById("preloader_message"))&&(r.innerHTML="- posting foto -");break;case"finishing":var r;(r=document.getElementById("preloader_message"))&&(r.innerHTML="- finishing -");break;case"destroy":var i=document.getElementById("personal_group_overlay"),a=document.getElementById("personal_group_preloader");i&&i.parentNode.removeChild(i),a&&a.parentNode.removeChild(a),document.body.style.overflow="visible"}}function show_image_name(e){"[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&e.target.files&&(document.getElementById("filename").innerHTML=e.target.value.replace(/^.*[\\\/]/,"").slice(0,30),e.target.files[0].size<20000001?window.FileReader&&window.Blob&&validate_img_file(e):throw_err(e.target,"size","pg_main"))}function validate_img_file(e){is_pub_grp_img?pub_grp_subform.disabled=!0:is_pub_img?pub_img_subform.disabled=!0:is_reply?rep_subform.disabled=!0:subform.disabled=!0;var t=e.target.files[0],r=new FileReader;r.onload=validate_file,r.readAsArrayBuffer(t.slice(0,4))}function validate_file(e){for(var t="",r=new Uint8Array(e.target.result),i=0;i<r.length;i++)t+=r[i].toString(16);switch(t){case"89504e47":is_pub_grp_img?valid_pub_grp_img="png":is_pub_img?valid_public_img="png":is_reply?valid_rep_img="png":valid_img="png";break;case"47494638":is_pub_grp_img?valid_pub_grp_img="gif":is_pub_img?valid_public_img="gif":is_reply?valid_rep_img="gif":valid_img="gif";break;case"ffd8ffe0":case"ffd8ffe1":case"ffd8ffe2":case"ffd8ffe3":case"ffd8ffe8":case"ffd8ffdb":is_pub_grp_img?valid_pub_grp_img="jpeg":is_pub_img?valid_public_img="jpeg":is_reply?valid_rep_img="jpeg":valid_img="jpeg";break;default:is_pub_grp_img?throw_err(pub_grp_browse_image_btn,"mime","pub_grp_img"):is_pub_img?(valid_public_img=null,throw_err(browse_pub_img_btn,"mime","public_img")):is_reply?(valid_rep_img=null,throw_err(browse_rep_image_btn,"mime","pg_reply")):throw_err(browse_image_btn,"mime","pg_main")}is_pub_grp_img?(pub_grp_subform.disabled=!1,is_pub_grp_img=!1):is_pub_img?(pub_img_subform.disabled=!1,is_pub_img=!1):is_reply?(rep_subform.disabled=!1,is_reply=!1):subform.disabled=!1}function process_ajax(e,t,r,i,a,n,_,o,l,p){var m=new FormData;e&&m.append(l,e),a&&m.append("resized","1"),n&&m.append("reoriented","1"),"pg_main"===_?(m.append("tid",document.getElementById("tid").value),m.append("sk",document.getElementById("sk").value)):"public_img"===_?m.append("sk",document.getElementById("pub_img_sk").value):"pg_reply"===_?(m.append("tt",document.getElementById("rep_tt").value),m.append("bid",document.getElementById("rep_bid").value),m.append("idx",document.getElementById("rep_idx").value),m.append("tid",document.getElementById("rep_tid").value),m.append("sk",document.getElementById("rep_sk").value)):(m.append("gp",document.getElementById("pub_grp_subform").value),m.append("sk",document.getElementById("pub_grp_sk").value)),m.append(o,i,t),personal_group_preloader("update");var d=new XMLHttpRequest;d.open("POST",r),d.timeout=45e3,d.setRequestHeader("X-CSRFToken",get_cookie("csrftoken")),d.setRequestHeader("X-Requested-With","XMLHttpRequest"),d.onload=function(){if(200==this.status){var e=JSON.parse(this.responseText);window.location.replace(e.message),personal_group_preloader("destroy")}else window.location.replace("/missing/"),personal_group_preloader("destroy")},d.onerror=function(){window.location.replace(p),personal_group_preloader("destroy")},d.onprogress=function(){personal_group_preloader("finishing")},d.ontimeout=function(e){window.location.replace(p),personal_group_preloader("destroy")},d.send(m)}function personal_group_submit(e){!browse_image_btn.files[0]||!valid_img||detect_android_ver()<4.1||(e.preventDefault(),personal_group_preloader("create"),prep_image(browse_image_btn.files[0],text_field.value,browse_image_btn.files[0].name,e.target.action,"pg_main","image","reply","/private_chat/",null,process_ajax))}function prep_image(e,t,r,i,a,n,_,o,l,p){get_orientation(e,a,function(m){var d=document.createElement("img"),g=new FileReader;g.onload=function(){var s=g.result;d.onload=function(){img_width=this.width,img_height=this.height,img_to_send=resize_and_compress(this,img_width,img_height,"image/jpeg",m,l),img_to_send.size>e.size?p(t,r,i,e,!1,!1,a,n,_,o):p(t,r,i,img_to_send,!0,!0,a,n,_,o)},d.onerror=function(){window.location.href=window.location.href,personal_group_preloader("destroy")},d.src=s},g.readAsDataURL(e)})}function resize_and_compress(e,t,r,i,a,n){switch(a){case 2:case 3:case 4:break;case 5:case 6:case 7:case 8:var _;_=t,t=r,r=_}var o=null;if(n)o=n;else switch(!0){case t<wranges[4]:case t<wranges[3]:o=wranges[4];break;case t<wranges[2]:o=wranges[3];break;case t<wranges[1]:o=wranges[2];break;case t<wranges[0]:o=wranges[1];break;default:o=wranges[0]}var l=o/t,p=Math.round(r*l),m=document.createElement("canvas");m.width=o,m.height=p;var d=m.getContext("2d");switch(a){case 2:d.translate(o,0),d.scale(-1,1);break;case 3:d.translate(o,p),d.rotate(-Math.PI);break;case 4:d.translate(0,p),d.scale(1,-1);break;case 5:d.rotate(.5*Math.PI),d.scale(p/o,-o/p);break;case 6:d.rotate(.5*Math.PI),d.translate(0,-o),d.scale(p/o,o/p);break;case 7:d.rotate(.5*Math.PI),d.translate(p,-o),d.scale(-p/o,o/p);break;case 8:d.translate(0,p),d.scale(o/p,p/o),d.rotate(-.5*Math.PI)}return d.drawImage(e,0,0,o,p),dataURItoBlob(m.toDataURL(i),i)}function dataURItoBlob(e,t){for(var r=atob(e.split(",")[1]),i=new ArrayBuffer(r.length),a=new Uint8Array(i),n=0;n<r.length;n++)a[n]=r.charCodeAt(n);return new Blob([i],{type:t})}function get_cookie(e){if(!e)return null;var t=("; "+document.cookie).split("; "+e+"=");return t.length>=2?t.pop().split(";").shift():void 0}function throw_err(e,t,r){"pub_grp_img"==r?(target_elem="size"==t?document.getElementById("pub_grp_img_size_err"):document.getElementById("pub_grp_img_mime_err"),pub_grp_form.insertAdjacentElement("afterbegin",target_elem)):"public_img"==r?(target_elem="size"==t?document.getElementById("pub_img_size_err"):document.getElementById("pub_img_mime_err"),public_photo_form.insertAdjacentElement("afterbegin",target_elem)):"pg_reply"==r?(target_elem="size"==t?document.getElementById("pg_rep_size_err"):document.getElementById("pg_rep_mime_err"),form_template.insertAdjacentElement("afterbegin",target_elem)):(top_elem=document.getElementById("personal_group_top"),target_elem="size"==t?document.getElementById("pg_size_err"):document.getElementById("pg_mime_err"),top_elem&&(top_elem.innerHTML="",top_elem.insertAdjacentElement("afterbegin",target_elem))),target_elem.style.display=null,e.value=""}function get_orientation(e,t,r){if("pg_reply"===t){if("jpeg"!=valid_rep_img)return r(-2)}else if("pub_grp_img"===t){if("jpeg"!=valid_pub_grp_img)return r(-2)}else if("public_img"===t){if("jpeg"!=valid_public_img)return r(-2)}else if("jpeg"!=valid_img)return r(-2);var i=new FileReader;i.onload=function(e){var t=new DataView(e.target.result);if(65496!=t.getUint16(0,!1))return r(-2);for(var i=t.byteLength,a=2;a<i;){if(t.getUint16(a+2,!1)<=8)return r(-1);var n=t.getUint16(a,!1);if(a+=2,65505==n){if(1165519206!=t.getUint32(a+=2,!1))return r(-1);var _=18761==t.getUint16(a+=6,!1);a+=t.getUint32(a+4,_);var o=t.getUint16(a,_);a+=2;for(var l=0;l<o;l++)if(274==t.getUint16(a+12*l,_))return r(t.getUint16(a+12*l+8,_))}else{if(65280!=(65280&n))break;a+=t.getUint16(a,!1)}}return r(-1)},i.readAsArrayBuffer(e.slice(0,131072))}browse_image_btn&&(browse_image_btn.onchange=show_image_name),Blob=function(){var e=Blob;return Blob.prototype.webkitSlice?Blob.prototype.slice=Blob.prototype.webkitSlice:Blob.prototype.mozSlice&&(Blob.prototype.slice=Blob.prototype.mozSlice),function(t,r){try{return Blob=e,new Blob(t||[],r||{})}catch(e){Blob=function(e,t){var r,i=new(WebKitBlobBuilder||MozBlobBuilder);for(r in e)i.append(e[r]);return i.getBlob(t&&t.type?t.type:void 0)}}}}();var is_reply=!1,valid_rep_img=!1,rep_btns=document.querySelectorAll("button.rep");form_template&&(form_template.onsubmit=personal_group_reply_submit);var browse_rep_image_btn=document.getElementById("browse_rep_image_btn");browse_rep_image_btn&&(browse_rep_image_btn.onchange=show_rep_image_name);for(var i=0,len=rep_btns.length;i<len;i++)rep_btns[i].onclick=toggle_rep;function show_rep_image_name(e){"[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&e.target.files&&(document.getElementById("pg_rep_size_err").style.display="none",document.getElementById("pg_rep_mime_err").style.display="none",document.getElementById("rep_filename").innerHTML=e.target.value.replace(/^.*[\\\/]/,"").slice(0,15),e.target.files[0].size<20000001?window.FileReader&&window.Blob&&(is_reply=!0,validate_img_file(e)):(valid_rep_img=null,throw_err(e.target,"size","pg_reply")))}function populate_input_fields(e,t,r){var i=document.getElementById("rep_tt");i.value=e;var a=new UIEvent("change",{view:window,bubbles:!0,cancelable:!0});i.dispatchEvent(a);var n=document.getElementById("rep_bid");n.value=t;var _=new UIEvent("change",{view:window,bubbles:!0,cancelable:!0});n.dispatchEvent(_);var o=document.getElementById("rep_idx");o.value=r;var l=new UIEvent("change",{view:window,bubbles:!0,cancelable:!0});o.dispatchEvent(l)}function empty_input_fields(){var e=document.getElementById("rep_tt");e.value="";var t=new UIEvent("change",{view:window,bubbles:!0,cancelable:!0});e.dispatchEvent(t);var r=document.getElementById("rep_bid");r.value="";var i=new UIEvent("change",{view:window,bubbles:!0,cancelable:!0});r.dispatchEvent(i);var a=document.getElementById("rep_idx");a.value="";var n=new UIEvent("change",{view:window,bubbles:!0,cancelable:!0});a.dispatchEvent(n)}function personal_group_reply_submit(e){if(!(detect_android_ver()<4.1))return valid_rep_img?(e.preventDefault(),personal_group_preloader("create"),void prep_image(browse_rep_image_btn.files[0],rep_text_field.value,browse_rep_image_btn.files[0].name,e.target.action,"pg_reply","rep_image","rep_reply","/private_chat/",null,process_ajax)):null==valid_rep_img?void e.preventDefault():void 0}function toggle_rep(e){if(form_template&&"[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&!(detect_android_ver()<4.1)){e.preventDefault();var t=this.parentNode.querySelector("#payload").value.split(":"),r=t[5],i=t[0],a=t[3],n=this.parentNode.nextElementSibling;null==n&&(form_template.style.display="inline",empty_input_fields(),e.target.parentNode.insertAdjacentElement("afterend",form_template),populate_input_fields(r,i,a)),null!=n&&"form_template"==n.id&&"inline"==form_template.style.display?(form_template.style.display="none",empty_input_fields()):(form_template.style.display="inline",empty_input_fields(),e.target.parentNode.insertAdjacentElement("afterend",form_template),populate_input_fields(r,i,a))}}var is_pub_img=!1,valid_public_img=!1,public_photo_form=document.getElementById("public_photo_form");public_photo_form&&(public_photo_form.onsubmit=public_photo_submit);var public_photo_upload_btn=document.getElementById("browse_pub_img_btn");function validate_public_image(e){"[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&e.target.files&&(document.getElementById("pub_img_size_err").style.display="none",document.getElementById("pub_img_mime_err").style.display="none",e.target.files[0].size<20000001?window.FileReader&&window.Blob&&(is_pub_img=!0,validate_img_file(e)):(valid_public_img=null,throw_err(e.target,"size","public_img")))}function public_photo_submit(e){if(!(detect_android_ver()<4.1))return valid_public_img?(e.preventDefault(),personal_group_preloader("create"),void prep_image(browse_pub_img_btn.files[0],pub_img_caption_field.value,browse_pub_img_btn.files[0].name,e.target.action,"public_img","image_file","caption","/upload_public_photo/",400,process_ajax)):null==valid_public_img?void e.preventDefault():void 0}public_photo_upload_btn&&(public_photo_upload_btn.onchange=validate_public_image);var is_pub_grp_img=!1,valid_pub_grp_img=!1,pub_grp_form=document.getElementById("pub_grp_form");pub_grp_form&&(pub_grp_form.onsubmit=pub_grp_form_submit);var pub_grp_browse_image_btn=document.getElementById("pub_grp_browse_image_btn");function validate_pub_grp_img(e){"[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&e.target.files&&(document.getElementById("pub_grp_img_size_err").style.display="none",document.getElementById("pub_grp_img_mime_err").style.display="none",e.target.files[0].size<20000001?window.FileReader&&window.Blob&&(is_pub_grp_img=!0,validate_img_file(e)):throw_err(e.target,"size","pub_grp_img"))}function pub_grp_form_submit(e){detect_android_ver()<4.1||valid_pub_grp_img&&(e.preventDefault(),personal_group_preloader("create"),prep_image(pub_grp_browse_image_btn.files[0],pub_grp_text_field.value,pub_grp_browse_image_btn.files[0].name,e.target.action,"pub_grp_img","image","text","/mehfil/awami/",400,process_ajax))}pub_grp_browse_image_btn&&(pub_grp_browse_image_btn.onchange=validate_pub_grp_img);