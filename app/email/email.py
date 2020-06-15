"""
Implement here.
"""
from threading import Thread
from flask_mail import Message
from flask import current_app
from app import mail


def send_async_message(app, message):
    with app.app_context():
        mail.send(message)


def send_email(subject, sender, recipient, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipient)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_message,
           args=(current_app._get_current_object(), msg)).start()
