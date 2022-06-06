import logging

from celery import shared_task
from django.utils.translation import gettext as _

from ....models import InsightAccountInactive
from ....dudes import InsightAccountInactiveDude

logger = logging.getLogger(__name__)


@shared_task
def insight_account_inactive_delete_accounts(insight_account_inactive_id):
    """
    Remove found inactive accounts linked to insight_account_inactive object
    :param insight_account_inactive_id: InsightAccountInactive.id
    :return: string - number of inactive a inactive accounts removed
    """
    insight_account_inactive = InsightAccountInactive.objects.get(id=insight_account_inactive_id)
    count_deleted_accounts = insight_account_inactive.delete_inactive_accounts()

    return _(f"Deleted {count_deleted_accounts} inactive accounts")


@shared_task
def insight_account_inactive_populate_accounts(insight_account_inactive_id):
    """
    Find inactive accounts on a given date and add them to the InsightAccountInactiveAccount model
    :param insight_account_inactive_id: InsightAccountInactive.id
    :return: string - number of inactive accounts found & added to list
    """
    insight_account_inactive = InsightAccountInactive.objects.get(id=insight_account_inactive_id)
    insight_account_inactive_dude = InsightAccountInactiveDude()

    count_inactive_accounts = \
        insight_account_inactive_dude.populate_accounts_for_insight_account_inactive_from_date(
            insight_account_inactive
        )

    return _(f'Found {count_inactive_accounts} inactive accounts')
