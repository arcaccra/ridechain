from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

def send_templated_email(recipient_list, template_name, subject, context):
    try:
        html_content = render_to_string(template_name, context)
        text_content = "This email requires an HTML-compatible email client."  # Or render a plain text template if you have one

        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_welcome_email(recipient_list, username):
    context = {'username': username}
    return send_templated_email(recipient_list, 'welcome_email.html', "Welcome to our platform!", context)


def send_verification_email(recipient_list, verification_url):
    context = {'verification_url': verification_url}
    return send_templated_email(recipient_list, 'verification_email.html', "Verify Your Email", context)