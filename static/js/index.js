	const registerSw = async () => {
    if ('serviceWorker' in navigator) {
        const reg = await navigator.serviceWorker.register('sw.js');
        initialiseState(reg)

    } else {
        showNotAllowed("You can't send push notifications.")
    }
}

const initialiseState = (reg) => {
    if (!reg.showNotification) {
        showNotAllowed('Showing notifications isn\'t supported');
        return
    }
    if (Notification.permission === 'denied') {
        showNotAllowed('You prevented us from showing notifications');
        return
    }
    if (!'PushManager' in window) {
        showNotAllowed("Push isn't allowed in your browser");
        return
    }
    subscribe(reg);
}

const showNotAllowed = (message) => {
    alert(`${message}`)
};

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));

    return outputData;
}

const subscribe = async (reg) => {
    const subscription = await reg.pushManager.getSubscription();
    if (subscription) {
        sendSubData(subscription);
        return;
    }

    const vapidMeta = document.querySelector('meta[name="vapid-key"]');
    const key = vapidMeta.content;
    const options = {
        userVisibleOnly: true,
        // if key exists, create applicationServerKey property
        ...(key && {applicationServerKey: urlB64ToUint8Array(key)})
    };

    const sub = await reg.pushManager.subscribe(options);
    sendSubData(sub)
};

const sendSubData = async (subscription) => {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: 'subscribe',
        subscription: subscription.toJSON(),
        browser: browser,
    };

    const res = await fetch('/webpush/save_information', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json'
        },
        credentials: "include"
    });

    handleResponse(res);
};

const handleResponse = (res) => {
    console.log(res.status);
};

registerSw()


	function openChat(e){
	    fetch(`${location.origin}/create-room/`)
		.then((res)=>{
		    return res.json()
		})
		.then((result)=>{
		})

	    e.target.parentElement.nextElementSibling.style.display = 'block'
	}

	function closeChat(e){
	    document.getElementById('chatDiv').style.display = 'none'

	}
	    setTimeout(()=>{
        document.getElementById('pop-up').style.display = 'block'
    },10000)
	function closePopup(e){
    const chatDiv = document.getElementById('chat-face')
	    document.getElementById('pop-up').style.display = 'none'
        chatDiv.style.top = 5+'px'
        chatDiv.style.bottom = 0+'px'
        chatDiv.style.right = 20+'px'
	}

      function cart_count(e){
            const num = document.getElementsByClassName('cart_count')
            const base_url = `${origin}/cart-count/`
            fetch(base_url)
            .then((res)=>{
                return res.json()
            })
            .then((result)=>{
                for (let i=0;i<num.length;i++){
                    num[i].innerHTML = result.Count

                }
            })

}


        function mobile_click(e) {
        const menu = document.getElementById('menu_div')
		if (menu.style.visibility === 'hidden') {

            menu.style.height = 100+'%'
            menu.classList.remove('fade-out-menu')
            menu.classList.add('fade-in-menu','p-5')
            menu.style.visibility = 'visible'
        }
        else{

            menu.style.height = 0

            menu.classList.remove('fade-in-menu','p-5')
            menu.classList.add('fade-out-menu')
            menu.style.visibility = 'hidden'
        }

    }

      if (window.innerWidth<1161) {
        const pay = document.getElementById('pay')
            pay.style.height = 35 + 'px'
            pay.style.width = 90 + '%'

    }

      function search(e){
        function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
        const csrftoken = getCookie('csrftoken');
        const base_url = `${origin}/search/`
        const varData = new FormData()
        varData.append('value',e.target.previousElementSibling.value)
        fetch(base_url,{
            method:'POST',
            body:JSON.stringify({'search':e.target.previousElementSibling.value}),
        headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken,'X-Requested-With':'XMLHttpRequest'}
        })
        .then(()=>{
            return
        })
        .then((res)=>{
            return
        })

    }

      let ChatEnable = false
    // export default ChatEnable