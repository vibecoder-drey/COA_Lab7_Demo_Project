'use strict';
const $=s=>document.querySelector(s);
const $$=s=>Array.from(document.querySelectorAll(s));
let dataState=null;
const logItems=[];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function showTab(tab){
  $$('.nav-btn').forEach(b=>{let on=b.dataset.target===tab;b.classList.toggle('active',on);if(on)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});
  $$('.panel').forEach(p=>{let on=p.id==='panel-'+tab;p.hidden=!on;p.classList.toggle('active',on)});
  window.scrollTo({top:0,behavior:'auto'});
}
$$('.nav-btn').forEach(btn=>btn.addEventListener('click',()=>showTab(btn.dataset.target)));
function formJSON(form){
  const o={};new FormData(form).forEach((v,k)=>{if(!(v instanceof File))o[k]=v});
  form.querySelectorAll('input[type=checkbox]').forEach(i=>o[i.name]=i.checked);
  return o;
}
function alertFor(form,text,success=false){const box=$('#'+form.id.slice(5)+'-alert');box.textContent=text;box.hidden=false;box.classList.toggle('success',success);}
function clearAlert(form){const box=$('#'+form.id.slice(5)+'-alert');box.textContent='';box.hidden=true;box.classList.remove('success');form.querySelectorAll('.invalid').forEach(e=>{e.classList.remove('invalid');e.removeAttribute('aria-invalid')});}
function markInvalid(el){el.classList.add('invalid');el.setAttribute('aria-invalid','true');}
function clientValidate(form){
  clearAlert(form);
  const invalid=[];
  for(const field of Array.from(form.elements)){
    if(!(field instanceof HTMLElement)||!('willValidate' in field)||!field.willValidate)continue;
    if(!field.checkValidity()){markInvalid(field);const label=field.id&&form.querySelector('label[for="'+field.id+'"]');invalid.push(label?label.textContent.replace('*','').trim():(field.name||'Required field'));}
  }
  if(form.id==='form-dependent'){
    const file=$('#d-file').files[0];
    if(file&&(!/\.(png|jpe?g|pdf)$/i.test(file.name)||file.size>1024*1024)){markInvalid($('#d-file'));invalid.push('Valid PDF/PNG/JPEG file under 1 MB')}
    if(dataState&&dataState.dependents.length>=4)invalid.push('Maximum of four dependents');
  }
  if(form.id==='form-appointment'){
    const dt=$('#a-day').value;if(dt&&dt<=new Date().toLocaleDateString('en-CA')){markInvalid($('#a-day'));invalid.push('Future appointment date')}
  }
  if(form.id==='form-search'){
    const start=$('#s-from').value,end=$('#s-to').value;
    if(start&&end&&start>end){markInvalid($('#s-to'));invalid.push('Date range (start must not be after end)')}
  }
  if(invalid.length){alertFor(form,'Please correct: '+Array.from(new Set(invalid)).join('; ')+'.');form.querySelector('.invalid')?.focus();return false}
  return true;
}
async function post(path,body){const resp=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const o=await resp.json();if(!resp.ok)throw Error(o.error||'Unable to process request.');return o}
function note(message){logItems.unshift({message,time:new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})});$('#activity-log').innerHTML=logItems.slice(0,5).map(a=>`<div class="log"><b>${esc(a.time)} · Form submitted</b>${esc(a.message)}</div>`).join('')}
async function refreshState(){
 const r=await fetch('/api/state');dataState=await r.json();
 $('#dep-count').textContent=dataState.dependents.length+'/4';$('#apt-count').textContent=dataState.appointments.length;
 $('#dependents-list').innerHTML=dataState.dependents.map(d=>`<div class="person"><b>${esc(d.full_name)}</b><small>${esc(d.relationship)} · ${esc(d.eligibility)}</small></div>`).join('');
 $('#appointments-list').innerHTML=dataState.appointments.slice(0,3).map(a=>`<div class="appt"><b>${esc(a.treatment)}</b><small>${esc(a.day)} at ${esc(a.slot)} · ${esc(a.dentist)}</small><span class="pill">${esc(a.status)}</span></div>`).join('');
 const sel=$('#a-dep'),v=sel.value;sel.innerHTML='<option value="">Select dependent</option>'+dataState.dependents.map(d=>`<option value="${d.id}">${esc(d.full_name)}</option>`).join('');if(v)sel.value=v;
 for(const [key,val] of Object.entries(dataState.profile)){const el=$('#form-profile [name="'+key+'"]');if(el)el.value=val;}
}
for(const f of $$('form')){
 f.addEventListener('input',e=>{if(e.target.classList?.contains('invalid')){e.target.classList.remove('invalid');e.target.removeAttribute('aria-invalid')}});
 f.addEventListener('reset',()=>{setTimeout(()=>{clearAlert(f);if(f.id==='form-profile'&&dataState){for(const [key,val] of Object.entries(dataState.profile)){const el=f.querySelector('[name="'+key+'"]');if(el)el.value=val}}},0)});
}
$('#form-dependent').addEventListener('submit',async e=>{
 e.preventDefault();let f=e.currentTarget;if(!clientValidate(f))return;
 const obj=formJSON(f),file=$('#d-file').files[0];
 if(file){obj.proof_file={name:file.name,data:(await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(file)})).split(',')[1]}}
 try{let r=await post('dependents',obj);f.reset();alertFor(f,r.message,true);note(r.message);await refreshState()}catch(err){alertFor(f,err.message)}
});
$('#form-appointment').addEventListener('submit',async e=>{e.preventDefault();let f=e.currentTarget;if(!clientValidate(f))return;try{let r=await post('appointments',formJSON(f));f.reset();alertFor(f,r.message,true);note(r.message);await refreshState()}catch(err){alertFor(f,err.message)}});
$('#form-search').addEventListener('submit',async e=>{e.preventDefault();let f=e.currentTarget;if(!clientValidate(f))return;try{let r=await post('search',formJSON(f));alertFor(f,r.message,true);const el=$('#search-results');el.innerHTML=`<p class="summary">${esc(r.message)}</p>`+(r.records.length?`<table><thead><tr><th>Type</th><th>Name</th><th>Details</th><th>Status</th></tr></thead><tbody>${r.records.map(x=>`<tr><td>${esc(x.type)}</td><td>${esc(x.name)}</td><td>${esc(x.detail)}</td><td>${esc(x.status)}</td></tr>`).join('')}</tbody></table>`:'<p class="muted">No fictional records matched.</p>');note(r.message)}catch(err){alertFor(f,err.message)}});
$('#form-profile').addEventListener('submit',async e=>{e.preventDefault();let f=e.currentTarget;if(!clientValidate(f))return;try{let r=await post('profile',formJSON(f));alertFor(f,r.message,true);note(r.message);await refreshState()}catch(err){alertFor(f,err.message)}});
function setDateBounds(){const t=new Date();const d=new Date(t.getFullYear(),t.getMonth(),t.getDate()+1);const max=new Date(t.getFullYear(),t.getMonth(),t.getDate()+90);const iso=x=>`${x.getFullYear()}-${String(x.getMonth()+1).padStart(2,'0')}-${String(x.getDate()).padStart(2,'0')}`;$('#a-day').min=iso(d);$('#a-day').max=iso(max);$('#d-dob').max=iso(t)}
setDateBounds();refreshState().catch(()=>{const a=$('#dependent-alert');a.hidden=false;a.textContent='Unable to connect to the demo server. Start python server.py, then reload.'});
