for(var sv=!1,uv_cids={},dv_cids={},vbtns=document.getElementsByClassName("vbtn"),i=0,len=vbtns.length;i<len;i++)vbtns[i].onclick=cast_vote;function cast_vote(e){var n=e.currentTarget,t=n.name;if("[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&n.value&&t){e.preventDefault(),n.disabled=!0;var l=n.value.split(":"),o=l[0],d=l[1],r=l[2],a=(l[3],l[4],d.toString()),i=document.getElementById("uident");if(i&&i.value===r&&(sv=!0),"1"===o&&a in uv_cids)display_and_fade_out(u="Ap aik hi vote 2 bar nahi dal saktey",determine_pause_length(u)),sv=!1,n.disabled=!1;else if("0"===o&&a in dv_cids){display_and_fade_out(u="Ap aik hi vote 2 bar nahi dal saktey",determine_pause_length(u)),sv=!1,n.disabled=!1}else if("1"!==o&&"0"!==o){display_and_fade_out(u="Vote nahi dala ja saka",determine_pause_length(u)),sv=!1,n.disabled=!1}else if(sv){var u;display_and_fade_out(u="Apni post pe vote nahi karein",determine_pause_length(u)),sv=!1,n.disabled=!1}else{var s=n.form.lastElementChild.previousElementSibling,c=s.childNodes,m=c[0],p=c[1];if(voted=update_btn_content(o,m,p,s,s.style.color,p.innerHTML),o&&d){var y=new FormData;y.append(t,n.value);var _=new XMLHttpRequest;_.open("POST","/cast_vote/"),_.timeout=1e4,_.setRequestHeader("X-CSRFToken",get_cookie("csrftoken")),_.setRequestHeader("X-Requested-With","XMLHttpRequest"),_.onload=function(){if(n.disabled=!1,200==this.status){var e=JSON.parse(this.responseText);e.success?"1"===o?"new"===e.message?uv_cids[a]="1":"old"==e.message&&delete dv_cids[a]:"0"===o&&("new"===e.message?dv_cids[a]="0":"old"==e.message&&delete uv_cids[a]):"text"===e.type?(display_and_fade_out(e.message,determine_pause_length(e.message)),"1"===o?("3"===e.offence&&(uv_cids[a]="1"),update_btn_content("0",m,p,s,s.style.color,p.innerHTML)):("3"===e.offence&&(dv_cids[a]="0"),update_btn_content("1",m,p,s,s.style.color,p.innerHTML))):"redirect"==e.type&&window.location.replace(e.message)}else{var t="Kuch ghalat ho gaya, dubara try karein";display_and_fade_out(t,determine_pause_length(t)),update_btn_content("1"===o?"0":"1",m,p,s,s.style.color,p.innerHTML)}},_.onerror=function(){n.disabled=!1;var e="Kuch kharab ho gaya, dubara try karein";display_and_fade_out(e,determine_pause_length(e)),update_btn_content("1"===o?"0":"1",m,p,s,s.style.color,p.innerHTML)},_.onprogress=function(){},_.ontimeout=function(e){n.disabled=!1;var t="Internet slow hai, baad mein try karein";display_and_fade_out(t,determine_pause_length(t)),update_btn_content("1"===o?"0":"1",m,p,s,s.style.color,p.innerHTML)},_.send(y)}}}}function update_btn_content(e,t,n,l,o,d){var r=t.innerHTML;if("1"===e)if("999+"===r||"-999"==r);else{var a=(r=parseInt(r,10))+1;1===(t.innerHTML=a)&&"POINTS"===d?n.innerHTML="POINT":1!==a&&"POINT"===d&&(n.innerHTML="POINTS"),a<0&&"rgb(255, 99, 71)"!=o?l.style.color="rgb(255, 99, 71)":-1<a&&"rgb(24, 180, 136)"!=o&&(l.style.color="rgb(24, 180, 136)")}else if("0"===e)if("-999"===r||"999+"===r);else{a=(r=parseInt(r,10))-1;1===(t.innerHTML=a)&&"POINTS"===d?n.innerHTML="POINT":1!==a&&"POINT"===d&&(n.innerHTML="POINTS"),a<0&&"rgb(255, 99, 71)"!=o?l.style.color="rgb(255, 99, 71)":-1<a&&"rgb(24, 180, 136)"!=o&&(l.style.color="rgb(24, 180, 136)")}}function determine_pause_length(e){var t=e.length;if(t<9)return 350;var n=1+.5*((t-9)/(t+9)),l=Math.round(Math.pow(350,n));return 6e3<l?6e3:l}var report_btns=document.getElementsByClassName("report");for(i=0,len=report_btns.length;i<len;i++)report_btns[i].onclick=report_modal;function report_modal(e){var t=document.getElementById("report_popup");if("[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&e.currentTarget.value&&t){e.preventDefault();var n=e.currentTarget.value,l=n.substring(0,2);if("tx"===l||"im"===l||"pf"===l){if("tx"===l){var o="tx",d=document.getElementById("type_txt"),r=n.split("#",8),a=document.getElementById("tp"+r[2]);(u=document.getElementById("report_txt")).innerHTML='"'+r[7].substring(0,40)+' ..."',(s=document.getElementById("submitter")).innerHTML=r[3],(c=document.getElementById("report_label")).innerHTML="REPORT<br>TEXT",(m=document.getElementById("block_label")).innerHTML="BLOCK<br>USER";var i=r[4]}else if("pf"===l){o="pf",d=document.getElementById("type_pf"),r=n.split("#",5);(u=document.getElementById("report_pf")).src=r[4],(s=document.getElementById("user_profile")).innerHTML=r[3],(c=document.getElementById("report_label")).innerHTML="REPORT<br>USER",(m=document.getElementById("block_label")).innerHTML="BLOCK<br>USER";i=r[2]}else{var u,s,c,m;o="img",d=document.getElementById("type_img"),r=n.split("#",8);(u=document.getElementById("report_img")).src=r[5],(s=document.getElementById("uploader")).innerHTML=r[3],(c=document.getElementById("report_label")).innerHTML="REPORT<br>FOTO",(m=document.getElementById("block_label")).innerHTML="BLOCK<br>USER";i=r[4]}var p=document.getElementById("uident").value,y=document.createElement("div");if(y.id="personal_group_overlay",y.className="ovl",y.style.background="#000000",y.style.opacity="0.5",i===p){var _=document.getElementById("report_own_item");document.body.appendChild(y),d.style.display="block",_.style.display="block",t.style.display="block",document.getElementById("report_popup_x").onclick=function(){"tx"===o?u.innerHTML="":u.src="",s.innerHTML="",_.style.display="none",t.style.display="none",d.style.display="none",y.parentNode.removeChild(y)}}else{var v,g,b,f,E,I,B,T,h,k,L=document.getElementById("report_btn"),M=document.getElementById("block_btn");if(document.body.appendChild(y),t.style.display="block",d.style.display="block",L.style.display="block",M.style.display="block","tx"===l||"im"===l){if((v=document.getElementById("r_tp")).value=o,(g=document.getElementById("r_org")).value=r[1],(b=document.getElementById("r_obid")).value=r[2],(f=document.getElementById("r_oun")).value=r[3],(E=document.getElementById("r_ooid")).value=r[4],(I=document.getElementById("r_url")).value=r[5],(B=document.getElementById("r_lid")).value=r[6],(T=document.getElementById("r_cap")).value=r[7],(h=document.getElementById("b_tun")).value=r[3],document.getElementById("b_org").value=r[1],document.getElementById("b_lid").value=r[6],document.getElementById("b_obid").value=r[2],(k=document.getElementById("b_tid")).value="7f"+parseInt(r[4],10).toString(16)+":a",a&&a.value){var H=document.getElementById("b_top"),O=document.getElementById("r_top");O.value=a.value,H.value=a.value}}else(v=document.getElementById("r_tp")).value=o,(g=document.getElementById("r_org")).value=r[1],(b=document.getElementById("r_obid")).value=r[2],(f=document.getElementById("r_oun")).value=r[3],(E=document.getElementById("r_ooid")).value=r[2],(I=document.getElementById("r_url")).value=r[4],(B=document.getElementById("r_lid")).value="",(T=document.getElementById("r_cap")).value="",(h=document.getElementById("b_tun")).value=r[3],document.getElementById("b_org").value=r[1],document.getElementById("b_lid").value="",document.getElementById("b_obid").value=r[2],(k=document.getElementById("b_tid")).value="7f"+parseInt(r[2],10).toString(16)+":a";document.getElementById("report_popup_x").onclick=function(){"tx"===o?u.innerHTML="":u.src="",s.innerHTML="",c.innerHTML="",m.innerHTML="",t.style.display="none",d.style.display="none",L.style.display="none",M.style.display="none",y.parentNode.removeChild(y),v.value="",g.value="",T.value="",b.value="",f.value="",I.value="",B.value="",E.value="",O.value="",k.value="",h.value="",H.value=""}}}}}var link_btns=document.getElementsByClassName("link");for(i=0,len=link_btns.length;i<len;i++)link_btns[i].onclick=copy_url;function copy_url(e){if("[object OperaMini]"!==Object.prototype.toString.call(window.operamini)&&e.currentTarget.value){e.preventDefault();var t="https://damadam.pk/photo_detail/"+e.currentTarget.value,n=document.createElement("input");document.body.appendChild(n),n.setAttribute("id","copied_url"),document.getElementById("copied_url").value=t,n.select(),document.execCommand("copy"),document.body.removeChild(n),display_and_fade_out("Link copied",determine_pause_length("Link copied"))}}function display_and_fade_out(e,t){var n=document.getElementById("quick_prompt"),l=document.getElementById("quick_text");if(l&&(l.innerHTML=e),n){var o=n.style;o.display="block",o.opacity=1}l&&n&&setTimeout(function(){!function e(){(o.opacity-=.1)<0?o.display="none":setTimeout(e,30)}()},t)}function get_cookie(e){if(!e)return null;var t=("; "+document.cookie).split("; "+e+"=");return 2<=t.length?t.pop().split(";").shift():void 0}[Element.prototype,CharacterData.prototype].forEach(function(e){e.hasOwnProperty("previousElementSibling")||Object.defineProperty(e,"previousElementSibling",{configurable:!0,enumerable:!0,get:function(){for(var e=this;e=e.previousSibling;)if(1===e.nodeType)return e;return null},set:void 0})}),function(e){e&&e.prototype&&null==e.prototype.lastElementChild&&Object.defineProperty(e.prototype,"lastElementChild",{get:function(){for(var e,t=this.childNodes,n=t.length-1;e=t[n--];)if(1===e.nodeType)return e;return null}})}(window.Node||window.Element);