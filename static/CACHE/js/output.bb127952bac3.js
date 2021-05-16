const imgs_blog=document.getElementsByTagName('img')
if(window.innerWidth<839){for(let i=0;i<imgs_blog.length;i++){if(i>2){console.log(imgs_blog[i].style.width)
if(imgs_blog[i].style.width<500+'px'){imgs_blog[i].style.height=250+'px'
imgs_blog[i].style.width=60+'%'
continue}
imgs_blog[i].setAttribute('id','k_img')
imgs_blog[i].style.width=100+'%'}}};