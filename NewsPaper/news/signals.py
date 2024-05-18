from Python312.Lib.test.dtracedata import instance
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import *
from ..NewsPaper import settings


def send_notification(preview, pk, title, subscribers_emails):
    html_content = render_to_string(
        'flatpages/post_created_email.html',
        {
            'text': preview,
            'link': f'http://127.0.0.1:8000/news/{pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )


@receiver(post_save, sender=Post)
def news_created(instance, created, **kwargs):
    if not created:
        return

    emails = User.objects.filter(
        subscriptions__category=instance.category
    ).values_list('email', flat=True)

    subject = f'Новая заметка в категории {instance.category}'

    text_content = (
        f'Новость: {instance.name}\n'
        f'Тема: {instance.title}\n\n'
        f'Содержание: {instance.content}\n\n\n'
        f'Ссылка на новость: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )
    html_content = (
        f'Новость: {instance.name}<br>'
        f'Тема: {instance.title}<br><br>'
        f'<a href="http://127.0.0.1{instance.get_absolute_url()}">'
        f'Ссылка на заметку</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@receiver(m2m_changed, sender=PostCategory.through)
def notify_about_new_post(sender, instance, action, **kwargs):
    print('**************')
    print(f'post_created called with action:{action}')
    print('**************')
    # if kwargs['action'] == 'post_add':
    #     categories = instance.postCategory.all()
    #     subscribers_emails = []
    #     for cat in categories:
    #         subscribers = Subscription.objects.filter(category=cat)
    #         subscribers_emails += [subs.user.email for subs in subscribers]
    #
    # send_notification(instance.preview(), instance.pk, instance.title, subscribers_emails)
