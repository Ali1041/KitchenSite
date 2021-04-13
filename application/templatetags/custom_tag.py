from django import template
from application.models import *
from application.views import cart_count
import json

register = template.Library()


@register.simple_tag
def new_url(value, field_name, urlencode=None):
    url = f'?{field_name}={value}'

    if urlencode:
        querystring = urlencode.split('&')
        filtered_queryset = filter(lambda p: p.split('=')[0] != field_name, querystring)
        join_encode = '&'.join(filtered_queryset)
        url = f'{url}&{join_encode}'

    return url

# worktop template tag
@register.simple_tag
def my_worktops():
    return Worktop_category.objects.all()

# appliances template tag
@register.simple_tag
def my_appliances():
    return Category_Applianes.objects.all()

# accessories template tag
@register.simple_tag
def my_accessories():
    return AccessoriesType.objects.all()

# cart count template tag
@register.simple_tag
def my_cart(request):
    user_cart = cart_count(request)
    return json.loads(user_cart.content)['Count']

# canonical tag url
@register.simple_tag
def canonical_tag(request):
    return request.build_absolute_uri(request.path)