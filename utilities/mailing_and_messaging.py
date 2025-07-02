from django.core.mail import send_mail, EmailMessage
from django.conf import settings

class SendMail:
    """Sends mail using the django email backend."""

    def __init__(self, subject, message, from_email, recipient_list, fail_silently=False):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently

    def send_mail(self):
        """Sends a plain text email."""
        send_mail(self.subject, self.message, self.from_email, self.recipient_list, self.fail_silently)

    def send_html_mail(self, html_message):
        """Sends an HTML email."""
        msg = EmailMessage(self.subject, html_message, self.from_email, self.recipient_list)
        msg.content_subtype = 'html'
        msg.send(fail_silently=self.fail_silently)

    def send_attachment_mail(self, html_message, attachment_path, attachment_name):
        """Sends an email with an attachment."""
        msg = EmailMessage(self.subject, html_message, self.from_email, self.recipient_list)
        msg.content_subtype = 'html'
        msg.attach_file(attachment_path, attachment_name)
        msg.send(fail_silently=self.fail_silently)