import datetime
import logging

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext as _

from .....models import ScheduleItemAttendance
from .....dudes import DateToolsDude, MailDude

logger = logging.getLogger(__name__)


@shared_task
def account_trialpass_followup():
    """
    Find classes taken using a trialpass yesterday and send the followup email to the corresponding accounts
    :return:
    """
    date_dude = DateToolsDude()
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)

    schedule_item_attendances = ScheduleItemAttendance.objects.filter(
        date=yesterday,
        account_classpass__isnull=False,
        account_classpass__organization_classpass__trial_pass=True
    )

    mails_sent = 0
    for schedule_item_attendance in schedule_item_attendances:
        logger.info("Sent trialpass_followup mail to %s" % schedule_item_attendance.account.email)

        mail_dude = MailDude(account=schedule_item_attendance.account,
                             email_template="trialpass_followup")
        mail_dude.send()

        mails_sent += 1

    return _("Sent %s trialpass followup mails.") % mails_sent
