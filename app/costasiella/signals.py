from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.db.models import Q

from django.dispatch import receiver

from graphql_jwt.signals import token_issued
from graphql_jwt.refresh_token.signals import refresh_token_rotated

from allauth.account.signals import user_signed_up
from .models.account_accepted_document import AccountAcceptedDocument
from .models.organization_document import OrganizationDocument
from .models.choices.organization_document_types import get_organization_document_types


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_signed_up)
def new_signup(request, user, **kwargs):
    """
    Log acceptance of Privacy policy and terms and conditions (if any)
    """
    now = timezone.now()
    today = now.date()
    client_ip = get_client_ip(request)

    # Do initial user account setup
    # Add bank account & instructor profile related records
    user.new_account_setup()

    # Add accepted documents
    document_types = get_organization_document_types()
    for document_type in document_types:
        documents = OrganizationDocument.objects.filter((
            Q(document_type=document_type[0]) &
            Q(date_start__lte=today) &
            (Q(date_end__gte=today) | Q(date_end__isnull = True))
        ))

        for document in documents:
            accepted_document = AccountAcceptedDocument(
                account=user,
                document=document,
                client_ip=client_ip
            )
            accepted_document.save()


@receiver(token_issued)
def on_token_issue(sender, request, user, **kwargs):
    """ Update last_login on token issue """
    user.last_login = timezone.now()
    user.save()


@receiver(refresh_token_rotated)
def on_refresh_token_rotated(sender, request, refresh_token, refresh_token_issued, **kwargs):
    """ Revoke refresh tokens after usage to lessen chance of abuse"""
    refresh_token.revoke(request)
