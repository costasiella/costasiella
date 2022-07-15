from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404
from django.db.models import Q

from ..models import OrganizationDocument


# Create your views here.
def terms_and_conditions(request):
    now = timezone.now()
    today = now.date()

    qs = OrganizationDocument.objects.filter(
        Q(document_type="TERMS_AND_CONDITIONS") &
        Q(date_start__lte=today) &
        (Q(date_end__gte=today) | Q(date_end__isnull=True))
    )

    if qs.exists():
        document = qs.first()
        return redirect(document.document.url)
    else: 
        raise Http404(_("File not found..."))


def privacy_policy(request):
    now = timezone.now()
    today = now.date()

    qs = OrganizationDocument.objects.filter(
        Q(document_type="PRIVACY_POLICY") &
        Q(date_start__lte=today) &
        (Q(date_end__gte=today) | Q(date_end__isnull=True))
    )

    if qs.exists():
        document = qs.first()
        return redirect(document.document.url)
    else: 
        raise Http404(_("File not found..."))
