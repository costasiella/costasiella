import datetime

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import Q, Sum

from .....models import ScheduleItemAttendance
from .....dudes import DateToolsDude, MailDude

@shared_task
def account_trialpass_followup():
    """
    Find classes taken using a trialpass yesterday and send the followup email to the corresponding accounts
    :return:
    """

    date_dude = DateToolsDude()

    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    print(yesterday)

    schedule_item_attendances = ScheduleItemAttendance.objects.filter(
        date=yesterday,
        account_classpass__isnull=False,
        account_classpass__organization_classpass__trial_pass=True
    )

    mails_sent = 0
    for schedule_item_attendance in schedule_item_attendances:
        mail_dude = MailDude(account=schedule_item_attendance.account,
                             email_template="trialpass_followup")
        mail_dude.send()

        mails_sent += 1

    return _("Sent %s trialpass followup mails.") % mails_sent
