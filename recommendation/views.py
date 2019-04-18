from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.db import connection
from django.contrib.auth.models import User
from Shortest_job_first import settings


def send_email(request):
    plaintext = get_template('email_template.txt')
    htmltext = get_template('email_template.html')
    username = {'username': User.username}
    subject, from_email, to = 'hello', settings.EMAIL_HOST_USER, 'jeff_illini_2017@outlook.com'
    text_content = plaintext.render(username)
    html_content = htmltext.render(username)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return render(request, "jobsite/index.html")