import datetime
import logging

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Q, Sum

from ....models import AccountSubscription, InsightAccountInactive
from ....dudes import DateToolsDude, InsightAccountInactiveDude

logger = logging.getLogger(__name__)


@shared_task
def insight_account_inactive_populate_accounts(insight_account_inactive_id):
    """
    Find inactive accounts on a given date and add them to the InsightAccountInactiveAccount model
    :param insight_account_inactive_id: InsightAccountInactive.id
    :return: string - number of inactive accounts found & added
    """
    insight_account_inactive = InsightAccountInactive.objects.get(id=insight_account_inactive_id)
    insight_account_inactive_dude = InsightAccountInactiveDude()

    count_inactive_accounts = \
        insight_account_inactive_dude.populate_accounts_for_insight_account_inactive_from_date(
            insight_account_inactive
        )



    return _(f'Found {count_inactive_accounts} inactive accounts')
