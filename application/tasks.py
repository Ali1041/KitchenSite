from celery import shared_task
from application.emails import send_all_emails, send_scheduled_emails
from celery.utils.log import get_task_logger
from application.models import Cart
from datetime import datetime
from django.db.models import Count

logger = get_task_logger(__name__)


@shared_task
def send_emails(subject, html_content, email):
    return send_all_emails(subject, html_content, email)


@shared_task
def scheduled_emails():
    all_carts = Cart.objects.filter(date__lte=datetime.now(), checkedout=False).prefetch_related('user')
    annotated_users = all_carts.values('user__email').annotate(user_count=Count('user'))
    return send_scheduled_emails(annotated_users)