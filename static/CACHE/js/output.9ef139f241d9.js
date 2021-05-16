if(window.innerWidth<768){const row=document.getElementById('row').children
for(let i=0;i<row.length;i++){row[i].setAttribute('class','col-3 my-2')}}
function move_down(){window.scrollTo({top:650,behavior:'smooth'})}
function select_color(e){const loopDiv=document.getElementById('loop').children
for(let i=0;i<loopDiv.length;i++){loopDiv[i].style.display='none'}
const spanColor=document.getElementById('color')
const displayKitchenDiv=document.getElementById('impDiv')
const fetching=document.getElementById('fetch')
const div=document.getElementById('new')
const imgsDiv=document.getElementById('imgsDiv')
fetching.style.display='block'
displayKitchenDiv.style.display='block'
spanColor.innerHTML=e.target.nextElementSibling.innerHTML
const base_url=origin
fetch(`${base_url}/get-kitchens/${e.target.nextElementSibling.innerHTML}/`).then((res)=>{return res.json()}).then((result)=>{fetching.style.display='none'
const actualResult=result.kitchens
const color=result.color
const listcolor=Object.values(color[0])
listcolor[0].forEach((item)=>{const p=document.createElement('p')
p.style.width=30+'px'
p.style.height=30+'px'
p.style.backgroundColor=`var(--${item})`
div.append(p)})
listcolor[1].forEach((item)=>{const img=document.createElement('img')
img.src=item
img.style.width=70+'px'
img.style.height=70+'px'
imgsDiv.append(img)})
actualResult.forEach((item,index)=>{loopDiv[index].style.display='block'
const img=loopDiv[index].children[1].firstElementChild
const textDiv=loopDiv[index].children[0]
img.src=listcolor[1][0]
textDiv.children[0].innerHTML=item.kitchen_type__name
textDiv.children[0].style.color='rgb(46, 154, 135)'
textDiv.children[1].innerHTML=item.description
loopDiv[index].href=`${base_url}/kitchen-view/${item.kitchen_type__name}/${e.target.nextElementSibling.innerHTML}`
move_down()})})};