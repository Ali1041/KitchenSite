from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mass_mail


def send_all_emails(subject, html_content, email):
    html_content = render_to_string(html_content)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        None,
        [email]
    )
    email.attach_alternative(html_content, 'text/html')
    return email.send()


def send_scheduled_emails(user_dict):
    mass_mail_tuple = []
    for item in user_dict:
        mass_mail_tuple.append(('Cart Reminder',
                                f'There are {item["user_count"]} items in your cart, waiting for checkout', None,
                                [item['user__email'],'testingtakenornot1@gmail.com' ]))
    tuple(mass_mail_tuple)
    return send_mass_mail(mass_mail_tuple, fail_silently=True)
