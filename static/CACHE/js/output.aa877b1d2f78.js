function unit_change(e,pk,status){const p=document.getElementById('unit_info')
let qty=1
if(status==='change'){qty=e.target.value}
fetch(`${origin}/unit-change/${pk}/${status}/${qty}/`).then((res)=>{return res.json()}).then((result)=>{if(status==='change'){p.innerHTML='Updated!!'
p.style.color='green'}
else if(status==='delete'){p.innerHTML='Removed!!'
p.style.color='red'}
setTimeout(()=>{p.innerHTML=''
location.reload()},1500)})}
function remove_cart(e,pk,process,pro){const base_url=`${origin}/add-to-cart`;let p='';fetch(`${base_url}/${pro}/appliance/${pk}/1/${process}/`).then((res)=>{return res.json()}).then((result)=>{if(pro==='worktop'){p=document.getElementById('info_worktop')}
else if(pro==='appliance'){p=document.getElementById('info_app')}
else if(pro==='accessories'){p=document.getElementById('info_acc')}
else if(pro==='service'){p=document.getElementById('info_service')}
else{p=document.getElementById('info_kitchen')}
p.style.color='red'
p.innerHTML='Removed from cart!!!'
setTimeout(()=>{p.innerHTML=''
location.reload()},1500)})}
function changing(e,pk,name,status){const qty=e.target.value
const base_url=`${origin}/add-to-cart`
let p=''
fetch(`${base_url}/${name}/any/${pk}/${qty}/${status}`).then((res)=>{return}).then((result)=>{if(name==='worktop'){p=document.getElementById('info_worktop')
console.log('here')}
else if(name==='appliance'){p=document.getElementById('info_app')}
else if(name==='service'){p=document.getElementById('info_service')}
else if(name==='accessories'){p=document.getElementById('info_acc')}
else if(name==='kitchen'){p=document.getElementById('info_kitchen')}
p.innerHTML='Updated!!';p.style.color='green'
setTimeout(()=>{p.innerHTML=''
location.reload()},1500)})};