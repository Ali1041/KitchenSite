            const active = document.getElementsByClassName('get');
            active[0].classList.add('active');
            const select = document.getElementById('select').innerText;
            const value = select.split(' ');
            console.log(value);
            const div = document.getElementById('cart');

            function change_url(e,name) {

                const color = e;
                const kitchen = name
                const base_url = `${origin}/kitchen-view`
                location.replace(`${base_url}/${kitchen}/${color}/`)
            }

			window.addEventListener('load',()=>{
			    window.scrollTo({top:400,behavior:"smooth"})
			})

                        function displayImage(e){
	            const fixed = document.getElementById('fixed')
	            fixed.style.display = 'block'
	            fixed.lastElementChild.src = e.target.src

            }
            function removeImage(e){
                const fixed = document.getElementById('fixed')
	            fixed.style.display = 'none'

            }

            function stop(e, status, kit, pk, pro) {

                const qty = e.target.parentElement.parentElement.previousElementSibling.firstElementChild.value
                const base_url = `${origin}/add-to-cart`;
                let url = ''
                if (value.length>3){
                    url = `${base_url}/${value[2]} ${value[3]}/${kit}/${pk}/${qty}/${pro}/`;
                }
                else{
                    url = `${base_url}/${value[2]}/${kit}/${pk}/${qty}/${pro}/`;
                }
                fetch(url)
                    .then((res) => {
                        return res.json()
                    })
                    .then((result) => {
                        div.style.bottom = 10 + '%';

                        setTimeout(() => {
                            div.style.bottom = -10 + '%';
                        }, 1500);
                        e.target.style.color = 'lightgray';
                        const ls = localStorage.getItem('pk');
                        if (ls === pk) {
                            const val = parseInt(qty) + 1
                            e.target.parentElement.parentElement.previousElementSibling.firstElementChild.value = val
                        }
                        localStorage.setItem('pk', pk)
                        cart_count('e')

                        return result
                    })

            }
//
// 							const tr = document.createElement('tr')
// 							const td_img = document.createElement('td')
// 							const img = document.createElement('img')
// 							const td_name = document.createElement('td')
// 							const td_type = document.createElement('td')
// 							const td_des = document.createElement('td')
// 							const td_price = document.createElement('td')
// 							const td_qty = document.createElement('td')
// 							const inp = document.createElement('input')
// 							td.qty.append(inp)
// 							const td_icon = document.createElement('td')
// 							const a = document.createElement('a')
// 							const i = document.createElement('i')
// 							i.setAttribute('class','fa fa-cart')
// 							a.append(i)
// 							a.setAttribute('href',`${location.origin}/`)
// 							tr.appendChild(td_img)
// 							tr.appendChild(td_name)
// 							tr.appendChild(td_type)
// 							tr.appendChild(td_des)
// 							tr.appendChild(td_price)
// 							tr.appendChild(td_qty)
							// tr.append(td_icon)