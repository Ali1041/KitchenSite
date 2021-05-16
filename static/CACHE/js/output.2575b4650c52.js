if(window.innerWidth<1162){const mobileButtons=document.getElementsByClassName('display_b')
mobileButtons[0].style.display='none'
mobileButtons[1].style.display='flex'}
const width=document.getElementById('width')
width.parentElement.nextElementSibling.style.width=width.offsetWidth+'px'
if(window.innerWidth<1161){const brand=document.getElementById('brand')
const btn=document.getElementById('btn')
btn.classList.add('btn-sm')
brand.style.height=40+'px'
brand.style.width=100+'%'}
window.addEventListener('load',()=>{const vid=document.getElementById('afterVideo')
vid.src=`/static/videos/tkc%20kitchen.mp4`
vid.setAttribute('autoplay','true')})
const video=document.getElementById('video')
const video2=document.getElementById('video1')
window.addEventListener('scroll',()=>{const sides=video.getBoundingClientRect()
const sides1=video2.getBoundingClientRect()
if(sides.top>=0&&sides.left>=0&&sides.right<=(window.innerWidth||document.documentElement.clientWidth)&&sides.bottom<=(window.innerHeight||document.documentElement.clientHeight)){video.setAttribute('muted','muted')
video.play()}
if(sides1.top>=0&&sides1.left>=0&&sides1.right<=(window.innerWidth||document.documentElement.clientWidth)&&sides1.bottom<=(window.innerHeight||document.documentElement.clientHeight)){video2.muted=true
video2.setAttribute('muted','true')
video2.play()}})
function search(e){function getCookie(name){let cookieValue=null;if(document.cookie&&document.cookie!==''){const cookies=document.cookie.split(';');for(let i=0;i<cookies.length;i++){const cookie=cookies[i].trim();if(cookie.substring(0,name.length+1)===(name+'=')){cookieValue=decodeURIComponent(cookie.substring(name.length+1));break;}}}
return cookieValue;}
const csrftoken=getCookie('csrftoken');const base_url=`${origin}/search/`
const varData=new FormData()
varData.append('value',e.target.previousElementSibling.value)
fetch(base_url,{method:'POST',body:JSON.stringify({'search':e.target.previousElementSibling.value}),headers:{'Content-Type':'application/json','X-CSRFToken':csrftoken,'X-Requested-With':'XMLHttpRequest'}}).then(()=>{return}).then((res)=>{return})}
function my_func(e){let url=[];fetch(`${origin}/get-images/${e.target.text}/`).then((res)=>{return res.json()}).then((result)=>{const parseResult=JSON.parse(result)
parseResult.forEach((item)=>{url.push('https://storage.googleapis.com/kitchensite/'+item.fields.img)})})
setTimeout(()=>{const toDelete=document.getElementById('deleteId')
toDelete.innerHTML=''
url.forEach((item,index)=>{const div=document.createElement('div')
const img=document.createElement('img')
img.src=item
if(index===0){div.setAttribute('class','carousel-item active')}
else{div.setAttribute('class','carousel-item')}
img.setAttribute('class','d-block w-100')
img.setAttribute('id','k_img')
img.style.height=470+'px'
div.append(img)
toDelete.append(div)})},1000)};