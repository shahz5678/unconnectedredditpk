function cast_vote(o){var d=o.currentTarget;var j=d.name;if(Object.prototype.toString.call(window.operamini)==='[object OperaMini]'||!d.value||!j)return;o.preventDefault(),d.disabled=!0;var i=d.value.split(':');var e=i[0];var k=i[1];var p=i[2];var q=i[3];var r=i[4];var h=k.toString();var l=document.getElementById('uident');if(l&&l.value===p&&(sv=!0),e==='1'&&h in uv_cids){var c='Ap aik hi vote 2 bar nahi dal saktey';display_and_fade_out(c,determine_pause_length(c)),sv=!1,d.disabled=!1;}else if(e==='0'&&h in dv_cids){var c='Ap aik hi vote 2 bar nahi dal saktey';display_and_fade_out(c,determine_pause_length(c)),sv=!1,d.disabled=!1;}else if(e!=='1'&&e!=='0'){var c='Vote nahi dala ja saka';display_and_fade_out(c,determine_pause_length(c)),sv=!1,d.disabled=!1;}else if(sv){var c='Apni post pe vote nahi karein';display_and_fade_out(c,determine_pause_length(c)),sv=!1,d.disabled=!1;}else{var a=d.form.lastElementChild.previousElementSibling;var m=a.childNodes;var f=m[0];var b=m[1];if(voted=update_btn_content(e,f,b,a,a.style.color,b.innerHTML),e&&k){var n=new FormData();n.append(j,d.value);var g=new XMLHttpRequest();g.open('POST','/cast_vote/'),g.timeout=10000,g.setRequestHeader('X-CSRFToken',get_cookie('csrftoken')),g.setRequestHeader('X-Requested-With','XMLHttpRequest'),g.onload=function(){if(d.disabled=!1,this.status==200){var c=JSON.parse(this.responseText);c.success?e==='1'?c.message==='new'?uv_cids[h]='1':c.message=='old'&&delete dv_cids[h]:e==='0'&&(c.message==='new'?dv_cids[h]='0':c.message=='old'&&delete uv_cids[h]):c.type==='text'?(display_and_fade_out(c.message,determine_pause_length(c.message)),e==='1'?(c.offence==='3'&&(uv_cids[h]='1'),update_btn_content('0',f,b,a,a.style.color,b.innerHTML)):(c.offence==='3'&&(dv_cids[h]='0'),update_btn_content('1',f,b,a,a.style.color,b.innerHTML))):c.type=='redirect'&&window.location.replace(c.message);}else{var g='Kuch ghalat ho gaya, dubara try karein';display_and_fade_out(g,determine_pause_length(g)),e==='1'?update_btn_content('0',f,b,a,a.style.color,b.innerHTML):update_btn_content('1',f,b,a,a.style.color,b.innerHTML);}},g.onerror=function(){d.disabled=!1;var c='Kuch kharab ho gaya, dubara try karein';display_and_fade_out(c,determine_pause_length(c)),e==='1'?update_btn_content('0',f,b,a,a.style.color,b.innerHTML):update_btn_content('1',f,b,a,a.style.color,b.innerHTML);},g.onprogress=function(){},g.ontimeout=function(g){d.disabled=!1;var c='Internet slow hai, baad mein try karein';display_and_fade_out(c,determine_pause_length(c)),e==='1'?update_btn_content('0',f,b,a,a.style.color,b.innerHTML):update_btn_content('1',f,b,a,a.style.color,b.innerHTML);},g.send(n);}}}function update_btn_content(h,g,c,d,e,f){var b=g.innerHTML;if(h==='1'){if(!(b==='999+'||b=='-999')){b=parseInt(b,10);var a=b+1;g.innerHTML=a,a===1&&f==='POINTS'?c.innerHTML='POINT':a!==1&&f==='POINT'&&(c.innerHTML='POINTS'),a<0&&e!='rgb(255, 99, 71)'?d.style.color='rgb(255, 99, 71)':a>-1&&e!='rgb(24, 180, 136)'&&(d.style.color='rgb(24, 180, 136)');}}else if(h==='0'&&!(b==='-999'||b==='999+')){b=parseInt(b,10);var a=b-1;g.innerHTML=a,a===1&&f==='POINTS'?c.innerHTML='POINT':a!==1&&f==='POINT'&&(c.innerHTML='POINTS'),a<0&&e!='rgb(255, 99, 71)'?d.style.color='rgb(255, 99, 71)':a>-1&&e!='rgb(24, 180, 136)'&&(d.style.color='rgb(24, 180, 136)');}}function determine_pause_length(h){var a=h.length;var b=9;var c=350;var d=6000;if(a<b)return c;else{var f=(a-b)/(a+b);var g=1+0.5*f;var e=Math.round(Math.pow(c,g));return e>d?d:e;}}function report_modal(A){var j=document.getElementById('report_popup');if(Object.prototype.toString.call(window.operamini)==='[object OperaMini]'||!A.currentTarget.value||!j)return;A.preventDefault();var v=A.currentTarget.value;var i=v.substring(0,2);if(!(i==='tx'||i==='im'||i==='pf'))return;if(i==='tx'){var d='tx';var f=document.getElementById('type_txt');var a=v.split('#',8);var w=document.getElementById('tp'+a[2]);var b=document.getElementById('report_txt');b.innerHTML='"'+a[7].substring(0,40)+' ..."';var e=document.getElementById('submitter');e.innerHTML=a[3];var g=document.getElementById('report_label');g.innerHTML='REPORT<br>TEXT';var h=document.getElementById('block_label');h.innerHTML='BLOCK<br>USER';var k=a[4];}else if(i==='pf'){var d='pf';var f=document.getElementById('type_pf');var a=v.split('#',5);var b=document.getElementById('report_pf');b.src=a[4];var e=document.getElementById('user_profile');e.innerHTML=a[3];var g=document.getElementById('report_label');g.innerHTML='REPORT<br>USER';var h=document.getElementById('block_label');h.innerHTML='BLOCK<br>USER';var k=a[2];}else{var d='img';var f=document.getElementById('type_img');var a=v.split('#',8);var b=document.getElementById('report_img');b.src=a[5];var e=document.getElementById('uploader');e.innerHTML=a[3];var g=document.getElementById('report_label');g.innerHTML='REPORT<br>FOTO';var h=document.getElementById('block_label');h.innerHTML='BLOCK<br>USER';var k=a[4];}var G=document.getElementById('uident').value;var c=document.createElement('div');if(c.id='personal_group_overlay',c.className='ovl',c.style.background='#000000',c.style.opacity='0.5',k===G){var B=document.getElementById('report_own_item');document.body.appendChild(c),f.style.display='block',B.style.display='block',j.style.display='block',document.getElementById('report_popup_x').onclick=function(){d==='tx'?b.innerHTML='':d=='pf'?b.src='':b.src='',e.innerHTML='',B.style.display='none',j.style.display='none',f.style.display='none',c.parentNode.removeChild(c);};}else{var C=document.getElementById('report_btn');var D=document.getElementById('block_btn');if(document.body.appendChild(c),j.style.display='block',f.style.display='block',C.style.display='block',D.style.display='block',i==='tx'||i==='im'){var l=document.getElementById('r_tp');l.value=d;var m=document.getElementById('r_org');m.value=a[1];var n=document.getElementById('r_obid');n.value=a[2];var o=document.getElementById('r_oun');o.value=a[3];var p=document.getElementById('r_ooid');p.value=a[4];var q=document.getElementById('r_url');q.value=a[5];var r=document.getElementById('r_lid');r.value=a[6];var s=document.getElementById('r_cap');s.value=a[7];var t=document.getElementById('b_tun');t.value=a[3];var x=document.getElementById('b_org');x.value=a[1];var y=document.getElementById('b_lid');y.value=a[6];var z=document.getElementById('b_obid');z.value=a[2];var u=document.getElementById('b_tid');if(u.value='7f'+parseInt(a[4],10).toString(16)+':a',w&&w.value){var E=document.getElementById('b_top');var F=document.getElementById('r_top');F.value=w.value,E.value=w.value;}}else{var l=document.getElementById('r_tp');l.value=d;var m=document.getElementById('r_org');m.value=a[1];var n=document.getElementById('r_obid');n.value=a[2];var o=document.getElementById('r_oun');o.value=a[3];var p=document.getElementById('r_ooid');p.value=a[2];var q=document.getElementById('r_url');q.value=a[4];var r=document.getElementById('r_lid');r.value='';var s=document.getElementById('r_cap');s.value='';var t=document.getElementById('b_tun');t.value=a[3];var x=document.getElementById('b_org');x.value=a[1];var y=document.getElementById('b_lid');y.value='';var z=document.getElementById('b_obid');z.value=a[2];var u=document.getElementById('b_tid');u.value='7f'+parseInt(a[2],10).toString(16)+':a';}document.getElementById('report_popup_x').onclick=function(){d==='tx'?b.innerHTML='':b.src='',e.innerHTML='',g.innerHTML='',h.innerHTML='',j.style.display='none',f.style.display='none',C.style.display='none',D.style.display='none',c.parentNode.removeChild(c),l.value='',m.value='',s.value='',n.value='',o.value='',q.value='',r.value='',p.value='',F.value='',u.value='',t.value='',E.value='';};}}function copy_url(b){if(Object.prototype.toString.call(window.operamini)==='[object OperaMini]'||!b.currentTarget.value)return;b.preventDefault();var e='https://damadam.pk/photo_detail/'+b.currentTarget.value;var a=document.createElement('textarea');a.setAttribute('readonly',!0),a.setAttribute('contenteditable',!0),a.style.position='fixed',a.value=e,document.body.appendChild(a),a.select();const c=document.createRange();c.selectNodeContents(a);const d=window.getSelection();d.removeAllRanges(),d.addRange(c),a.setSelectionRange(0,a.value.length),document.execCommand('copy'),document.body.removeChild(a),display_and_fade_out('Link copied',determine_pause_length('Link copied'));}function display_and_fade_out(d,e){var b=document.getElementById('quick_prompt');var c=document.getElementById('quick_text');if(c&&(c.innerHTML=d),b){var a=b.style;a.display='block',a.opacity=1;}c&&b&&setTimeout(function(){(function b(){(a.opacity-=0.1)<0?a.display='none':setTimeout(b,30);}());},e);}function get_cookie(b){if(!b)return null;var c='; '+document.cookie;var a=c.split('; '+b+'=');return a.length>=2?a.pop().split(';').shift():void 0;}var sv=!1;var uv_cids={};var dv_cids={};var vbtns=document.getElementsByClassName('vbtn');for(var i=0,len=vbtns.length;i<len;i++)vbtns[i].onclick=cast_vote;var report_btns=document.getElementsByClassName('report');for(var i=0,len=report_btns.length;i<len;i++)report_btns[i].onclick=report_modal;var link_btns=document.getElementsByClassName('link');for(var i=0,len=link_btns.length;i<len;i++)link_btns[i].onclick=copy_url;(function(a){a.forEach(function(a){if(a.hasOwnProperty('previousElementSibling'))return;Object.defineProperty(a,'previousElementSibling',{configurable:!0,enumerable:!0,get:function(){var a=this;while(a=a.previousSibling)if(a.nodeType===1)return a;return null;},set:undefined});});}([Element.prototype,CharacterData.prototype]),function(a){a&&a.prototype&&a.prototype.lastElementChild==null&&Object.defineProperty(a.prototype,'lastElementChild',{get:function(){var a,b=this.childNodes,c=b.length-1;while(a=b[c--])if(a.nodeType===1)return a;return null;}});}(window.Node||window.Element));