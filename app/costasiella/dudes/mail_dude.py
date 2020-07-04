import html2text

from django.utils.translation import gettext as _
from django.core.mail import send_mail

# https://docs.djangoproject.com/en/2.2/topics/email/

from django.core.mail import send_mail

from .mail_template_dude import MailTemplateDude


class MailDude:
    def __init__(self,
                 account,
                 email_template,
                 **kwargs):
        self.account = account
        self.email_template = email_template
        self.kwargs = kwargs

    def send(self):
        """
        Actually send mail
        :return:
        """
        # Get rendered template
        template_dude = MailTemplateDude(
            email_template=self.email_template,
            **self.kwargs,
        )
        template = template_dude.render()
        print(template)
        message = html2text.html2text(template['html_message'])

        if template.get('error', False):
            # Don't send an email when we have a render error
            return

        # Send mail
        send_mail(
            subject=template['subject'],  # Later from template
            message=message,
            html_message=template['html_message'],
            from_email="info@openstudioproject.com",
            recipient_list=[self.account.email],
            fail_silently=False
        )
