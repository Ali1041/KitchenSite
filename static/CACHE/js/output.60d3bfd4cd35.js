const out_max=document.getElementById('output_max')
const out_min=document.getElementById('output_min')
function change(e){e.target.previousElementSibling.firstElementChild.innerHTML=parseInt(e.target.value)}
function add_cart_1(e,pk,process,pro){const base_url=`${origin}/add-to-cart`
let url=`${base_url}/${pro}/appliance/${pk}/1/${process}/`
if(e.target.innerText==='Order sample'){url=`${base_url}/${pro}/sample/${pk}/1/${process}/`}
fetch(url).then((res)=>{return res.url}).then((result)=>{const check=result.split('/')
if(check[3]==='login'){location.replace(result)}
else{const p=document.getElementById(`add${pk}`)
p.innerHTML='Added to cart!!'
setTimeout(()=>{p.innerHTML=''},1500)}
cart_count('e')})};