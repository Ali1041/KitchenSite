const video=document.getElementById('video1')
window.addEventListener('scroll',()=>{const sides=video.getBoundingClientRect()
if(sides.top>=0&&sides.left>=0&&sides.right<=(window.innerWidth||document.documentElement.clientWidth)&&sides.bottom<=(window.innerHeight||document.documentElement.clientHeight)){video.play()}});