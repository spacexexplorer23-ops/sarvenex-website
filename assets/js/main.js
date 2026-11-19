(function(){
var d=document,root=d.documentElement;
try{var t=localStorage.getItem('theme');if(t)root.dataset.theme=t}catch(e){}
var tg=d.getElementById('themeToggle'),ic=d.getElementById('themeIcon');
function sync(){if(ic)ic.textContent=root.dataset.theme==='dark'?'☀':'☾'}sync();
if(tg)tg.onclick=function(){root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem('theme',root.dataset.theme)}catch(e){}sync()};
var mb=d.getElementById('menuBtn'),ln=d.getElementById('links');
if(mb)mb.onclick=function(){var o=ln.classList.toggle('open');mb.setAttribute('aria-expanded',o)};
if(ln)ln.onclick=function(e){if(e.target.tagName==='A'){ln.classList.remove('open');if(mb)mb.setAttribute('aria-expanded',false)}};
var y=d.getElementById('year');if(y)y.textContent=new Date().getFullYear();
var tabs=d.querySelectorAll('.tab');
tabs.forEach(function(b){b.onclick=function(){tabs.forEach(function(x){x.setAttribute('aria-selected',x===b);d.getElementById(x.getAttribute('aria-controls')).hidden=x!==b})}});
d.querySelectorAll('.term-body div').forEach(function(l,i){setTimeout(function(){l.classList.add('on')},500+i*550)});
})();
