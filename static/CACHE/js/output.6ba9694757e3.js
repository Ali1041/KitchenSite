function img_change(e,name,color){const main=document.getElementById(`main${name}`)
const link=document.getElementById(`link${name}`)
const split=color.split(',')
const target_alt=e.target.alt.split('/')
const exactColor=split[target_alt[target_alt.length-1]].split("'")
link.href=`/kitchen-view/${name}/${exactColor[1]}/`
main.src=e.target.src};