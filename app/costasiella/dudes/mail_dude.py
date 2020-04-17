from django.utils.translation import gettext as _
from django.core.mail import send_mail

# https://docs.djangoproject.com/en/2.2/topics/email/

from django.core.mail import send_mail

from .mail_template_dude import MailTemplateDude

class MailDude:
    def __init__(self,
                 account,
                 email_template):
        self.account = account
        self.email_template = email_template

    def send(self):
        """
        Actually send mail
        :return:
        """
        # Get rendered template

        # Send mail
        send_mail(
            subject="Test",  # Later from template
            message="Message",
            html_message="<html>hello world</html>",
            from_email="info@openstudioproject.com",
            recipient_list=[self.account.email],
            fail_silently=False
        )
