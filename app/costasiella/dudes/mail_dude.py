import html2text
import logging

from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings

# https://docs.djangoproject.com/en/2.2/topics/email/

from .mail_template_dude import MailTemplateDude

logger = logging.getLogger(__name__)


class MailDude:
    def __init__(self,
                 account,
                 email_template,
                 **kwargs):
        self.account = account
        self.email_template = email_template
        self.kwargs = kwargs
        self.kwargs['account'] = self.account

    def send(self):
        """
        Actually send mail
        :return:
        """
        # Fetch organization for organization email
        from ..models import Organization
        organization = Organization.objects.get(pk=100)

        # Get rendered template
        template_dude = MailTemplateDude(
            email_template=self.email_template,
            **self.kwargs,
        )
        template = template_dude.render()
        message = html2text.html2text(template['html_message'])

        if template.get('error', False):
            # Don't send an email when we have a render error
            logger.warning("Error rendering template %s, mail not sent to %s" %
                           (self.email_template, self.account.email))
            return

        # Send mail
        # https://docs.djangoproject.com/en/5.1/topics/email/#send-mail
        sent_messages = send_mail(
            subject=template['subject'],  # Later from template
            message=message,
            html_message=template['html_message'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.account.email],
            fail_silently=False
        )

        # sent_messages = 0 on fail
        # or 1 on success
        return bool(sent_messages)
