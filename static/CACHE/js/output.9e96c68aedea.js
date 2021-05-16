const video=document.getElementById('video1')
const video3=document.getElementById('video3')
const video4=document.getElementById('video4')
window.addEventListener('scroll',()=>{const sides=video.getBoundingClientRect()
const side3=video3.getBoundingClientRect()
const side4=video3.getBoundingClientRect()
if(sides.top>=0&&sides.left>=0&&sides.right<=(window.innerWidth||document.documentElement.clientWidth)&&sides.bottom<=(window.innerHeight||document.documentElement.clientHeight)){video.play()}
if(side3.top>=0&&side3.left>=0&&side3.right<=(window.innerWidth||document.documentElement.clientWidth)&&side3.bottom<=(window.innerHeight||document.documentElement.clientHeight)){video3.play()}
if(side4.top>=0&&side4.left>=0&&side4.right<=(window.innerWidth||document.documentElement.clientWidth)&&side4.bottom<=(window.innerHeight||document.documentElement.clientHeight)){video4.play()}});