from django.conf import settings
import requests


def get_captcha(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    print(result, r)
    if result['success']:
        return True
    else:
        return False
