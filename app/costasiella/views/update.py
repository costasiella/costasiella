import datetime

from django.utils.translation import gettext as _

from math import ceil

from django.http import Http404, HttpResponse
from django.utils import timezone
from django.db.models import Q, Sum

from ..models import \
    AccountSubscription, \
    AccountSubscriptionCredit, \
    FinanceInvoiceGroup, \
    FinanceInvoiceGroupDefault, \
    FinanceQuoteGroup, \
    Organization, \
    ScheduleEventTicket, \
    SystemMailTemplate, \
    SystemNotification
from ..dudes import PermissionDude, SystemSettingDude, VersionDude


def update(request):
    """
    Update function
    """
    if not request.user:
        raise Http404(_("Page not found..."))

    # Fetch current version
    version_dude = VersionDude()
    current_version = float(version_dude.version)

    # compare version update
    if current_version < 2021.02:
        _update_to_2021_02()

    if current_version < 2021.03:
        _update_to_2021_03()

    if current_version < 2022.03:
        _update_to_2022_03()

    if current_version < 2022.05:
        _update_to_2022_05()

    if current_version < 2022.07:
        _update_to_2022_07()

    # Set latest version
    new_version = version_dude.update_version()
    # Ensure default permissions are in place
    permission_dude = PermissionDude()
    permission_dude.verify_system_permissions()

    return HttpResponse(
        _("Updated database to version: %s.%s" % (new_version['version'], new_version['version_patch']))
    )


def _update_to_2021_02():
    """
    Update to 2021.02
    :return: None
    """
    # Set default value for 'workflow_shop_subscription_payment_method' if not already set
    setting_dude = SystemSettingDude()
    setting_dude.safe_set(
        'workflow_shop_subscription_payment_method',
        'MOLLIE'
    )


def _update_to_2021_03():
    """
    Update to 2021.03
    :return: None
    """
    system_mail_template = SystemMailTemplate(
        id=110000,
        name="trialpass_followup",
        subject="Trialpass followup",
        title="Trialpass followup",
        description="",
        content="Dear {{account.first_name}}, <br><br> -- Please replace this text with your own to follow up on trial passes. --",
        comments=""
    )
    system_mail_template.save()


def _update_to_2022_03():
    """
    Update db values to 2022.03
    :return: None
    """
    # Save tickets to populate subtotal, tax and total fields
    schedule_event_tickets = ScheduleEventTicket.objects.all()
    for ticket in schedule_event_tickets:
        ticket.save()


def _update_to_2022_05():
    """
    Update db values to 2022.05
    :return: None
    """
    # Set default invoice group for PRODUCTS
    default_invoice_group = FinanceInvoiceGroup.objects.get(id=100)
    products_default = FinanceInvoiceGroupDefault(
        item_type="PRODUCTS",
        finance_invoice_group=default_invoice_group
    )
    products_default.save()

    # Create default quotes group
    default_quote_group = FinanceQuoteGroup(
        id=100,
        display_public=True,
        name="Default",
        next_id=1,
        expires_after_days=30,
        prefix="QUO",
        prefix_year=True,
        auto_reset_prefix_year=True,
    )
    default_quote_group.save()

    # Add order creation notification mail template
    mail_template_order_received = SystemMailTemplate(
        id=45000,
        name="notification_order_received",
        subject="New order received!",
        title="New order received!",
        description="<ul><li>Order #{{order.id}}</li><li>Date {{order_date}}</li></ul>",
        content="{{order_items}}",
        comments="",
    )
    mail_template_order_received.save()

    # Add notification for order received
    system_notification = SystemNotification(
        id=10000,
        name="order_received",
        system_mail_template=mail_template_order_received
    )
    system_notification.save()

    # Set default branding colors for organization
    organization = Organization.objects.get(id=100)
    organization.branding_color_background = "#F6F6F6"
    organization.branding_color_text = "#14213D"
    organization.branding_color_accent = "#1EE494"
    organization.branding_color_secondary = "#AA99AA"
    organization.save()

def _update_to_2022_07():
    """
    Update db values to 2022.07
    :return: None
    """
    ## Migrate to individual credits
    now = timezone.now()
    today = now.date()
    # Loop over all active account non-unlimited subscriptions
    # Credit for unlimited subscriptions
    account_subscriptions = AccountSubscription.objects.filter(
        Q(date_start__lte=today) &
        (Q(date_end__gte=today) | Q(date_end__isnull=True)),
        Q(organization_subscription__unlimited=False)
    )
    for account_subscription in account_subscriptions:
        ## Calculate expiration
        credit_validity = account_subscription.organization_subscription.credit_validity
        credit_expiration = today + datetime.timedelta(days=credit_validity)

        ## Count current total for each (rounded up)
        qs_add = AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            mutation_type="ADD"
        ).aggregate(Sum('mutation_amount'))
        qs_sub = AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            mutation_type="SUB"
        ).aggregate(Sum('mutation_amount'))

        total_add = qs_add['mutation_amount__sum'] or 0
        total_sub = qs_sub['mutation_amount__sum'] or 0

        # Round up to nearest int
        total_credits_to_add = ceil(total_add - total_sub)
        # Use a range to add individual credits
        for i in range(0, total_credits_to_add):
            # With expiration defined by organization subscription
            account_subscription_credit = AccountSubscriptionCredit(
                account_subscription=account_subscription,
                expiration=credit_expiration,
                description=_("Migrated from previous credit system")
            )
            account_subscription_credit.save()
