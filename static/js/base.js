const width = document.getElementById('width')
	width.parentElement.nextElementSibling.style.width = width.offsetWidth+'px'

      if (window.innerWidth<1161) {
        const brand = document.getElementById('brand')
		const btn = document.getElementById('btn')
	      btn.classList.add('btn-sm')
		    brand.style.height = 40 + 'px'
            brand.style.width = 100 + '%';
    }

    const video = document.getElementById('video')
    const video2 = document.getElementById('video1')
    const vid = document.getElementById('afterVideo')

    window.addEventListener('scroll',()=>{
            const sides = video.getBoundingClientRect()
            const sides1 = video2.getBoundingClientRect()
            const sides2 = vid.getBoundingClientRect()
        if (	sides.top >= 0 &&
        sides.left >= 0 &&
        sides.right <= (window.innerWidth || document.documentElement.clientWidth) &&
        sides.bottom <= (window.innerHeight || document.documentElement.clientHeight)){
            video.setAttribute('muted','muted')
            video.play()
        }
	    if (sides1.top >= 0 &&
        sides1.left >= 0 &&
        sides1.right <= (window.innerWidth || document.documentElement.clientWidth) &&
        sides1.bottom <= (window.innerHeight || document.documentElement.clientHeight)){
		    video2.muted = true
            video2.setAttribute('muted','true')
            video2.play()
        }
	    if (sides2.top >= 0 &&
        sides2.left >= 0 &&
        sides2.right <= (window.innerWidth || document.documentElement.clientWidth) &&
        sides2.bottom <= (window.innerHeight || document.documentElement.clientHeight)){
		    vid.muted = true
            vid.setAttribute('muted','true')
            vid.play()
        }
    })



