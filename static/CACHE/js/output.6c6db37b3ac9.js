const active=document.getElementsByClassName('get')
active[0].classList.add('active')
const select=document.getElementById('select').innerText
const value=select.split(' ')
const div=document.getElementById('cart')
function stop(e,status,kit,pk,pro){const qty=e.target.parentElement.parentElement.previousElementSibling.firstElementChild.value
const base_url=`${origin}/add-to-cart`
let url=`${base_url}/${value[2]}/${kit}/${pk}/${qty}/${pro}/`
fetch(url).then((res)=>{return res.json()}).then((result)=>{div.style.bottom=10+'%'
setTimeout(()=>{div.style.bottom=-10+'%'},1500)
e.target.style.color='lightgray'
const ls=localStorage.getItem('pk')
if(ls===pk){const val=parseInt(qty)+1
e.target.parentElement.parentElement.previousElementSibling.firstElementChild.value=val}
localStorage.setItem('pk',pk)
cart_count('e')
return result})}
function change_url(e){const color=e;const kitchen=``
const base_url=`${origin}/kitchen-view`
location.replace(`${base_url}/${kitchen}/${color}/`)}
window.addEventListener('load',()=>{window.scrollTo({top:400,behavior:"smooth"})});