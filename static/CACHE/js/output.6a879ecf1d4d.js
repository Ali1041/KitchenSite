const face=document.getElementsByClassName('facebook-this')
const twit=document.getElementsByClassName('tweet-this')
const pin=document.getElementsByClassName('pinterest-this')
const imgs=document.getElementsByClassName('inside_link')
face[0].children[0].innerHTML=''
face[0].children[0].append(imgs[0])
face[0].style.alignSelf='center'
twit[0].children[0].innerHTML=''
twit[0].children[0].append(imgs[1])
twit[0].style.alignSelf='center'
pin[0].children[0].innerHTML=''
pin[0].children[0].append(imgs[2])
pin[0].style.alignSelf='center'
function operation(e){if(e.target.value==='-'&&e.target.nextElementSibling.value!=='1'){const x=parseInt(e.target.nextElementSibling.value)
e.target.nextElementSibling.value=x-1}
else if(e.target.value==='+'){const x=parseInt(e.target.previousElementSibling.value)
e.target.previousElementSibling.value=x+1}}
function add_cart(e){const base_url=`${origin}/add-to-cart`
const product=``
const item_name=``
const process='create'
const item_id=``
const qty=e.target.previousElementSibling.previousElementSibling.children[1].value
fetch(`${base_url}/${product}/${item_name}/${item_id}/${qty}/${process}/`).then((res)=>{return res.url}).then((result)=>{const check=result.split('/')
if(check[3]==='login'){location.replace(result)}
else{const p=document.getElementById('p')
p.innerHTML='Added to cart!!!'
setTimeout(()=>{p.innerHTML='';},3000)}})
cart_count('e')};