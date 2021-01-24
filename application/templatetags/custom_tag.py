from django import template

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
