from django.conf import settings
import requests
from django.utils.html import strip_tags
import random
from application.models import WorkTop,Appliances,Cart
from django.http import JsonResponse

# captcha validation
def get_captcha(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    data = {
        'secret': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
        # 'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    if result['success']:
        return True
    else:
        return False


# generic error displaying
def display_error_messages(form):
    error_msg = []
    for field, errors in form.errors.items():
        text_only = strip_tags(errors)
        error_msg.append(f'Error on field "{field}". {text_only}')
    return error_msg


# random queryset
def random_queryset():
    # returning random samples of appliances and worktops
    random_sample = random.sample(list(WorkTop.objects.all()), 2)
    random_sample_2 = random.sample(list(Appliances.objects.all()), 2)
    return random_sample, random_sample_2


# counting of cart items
def cart_count(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'Count': Cart.objects.select_related('user').filter(user=request.user, checkedout=False).count()})
    else:
        return JsonResponse({'Count': 0})