import datetime
import io
import re

from django.db.models import Q
from django.conf import settings
from django.http import Http404, FileResponse
from django.utils.translation import gettext as _
import openpyxl

from ...models import Account, AccountClasspass, AccountSubscription, AccountSubscriptionPause, ScheduleItemEnrollment
from ...modules.graphql_jwt_tools import get_user_from_cookie


def _check_export_prerequisites() -> tuple:
    ok = True
    error_msg = ""
    if not hasattr(settings, "SPORTBIT_MAP_SUBSCRIPTIONS"):
        ok = False
        error_msg = "SPORTBIT_MAP_SUBSCRIPTIONS not found in settings"

    return ok, error_msg

def _export_excel_accounts_active_get_header_info() -> list[str]:
    # This header isn't translatable, as it's always supposed to be in Dutch.
    return [
        # Account
        'Inlog gegevens versturen J/N',
        'Datum inschrijving',
        'Voorletters',
        'Voornaam',
        'Tussenvoegsel',
        'Achternaam',
        'Geboortedatum',
        'Geslacht',
        'Straat',
        'Huisnummer',
        'Postcode',
        'Woonplaats',
        'Land',
        'Emailadres',
        'Telefoonnummer vast',
        'Telefoonnummer mobiel',
        'Noodnummer',
        'Bedrijfsnaam',
        'Btwnummer',
        'Extern Relatienummer',
        'IBAN',
        'BIC',
        'Naam rekeninghouder',
        'Mandaat ID',
        'Blessure/Lichamelijke klachten',
        'Startdatum blessure',
        # Subscription
        'Productnummer Abonnement',
        'Startdatum Abonnement',
        'Evt. Stopdatum Abonnement bij opzegging',
        'Evt. reden opzegging',
        'Evt. Verloopdatum contracttermijn',
        'Aantal reseterende credits van abonnementen waarop de credits niet wekelijks of maandelijks maar in 1x worden afgegeven',
        'Evt. Startdatum gepauzeerd termijn abonnement',
        'Evt. Activatiedatum Gepauzeerd Termijn Abonnement',
        'Evt. Pauzereden',
        'Korting %',
        'Abonnement reeds betaald tot',
        'Betaalwijze abonnement',
        # Class pass
        'Productnummer Rittenkaart',
        'Ingangsdatum Rittenkaart',
        'Verloopdatim Rittenkaart',
        'Openstaande ritten',
        # Other
        'Familieaccount',
        'Vaste les',
        'Notities voor in klantenkaard lid',
    ]


def export_excel_sportbit_manager(request,**kwargs) -> FileResponse:
    """
    Export active accounts
    """
    user = get_user_from_cookie(request)
    if not user.has_perm('costasiella.view_account'):
        raise Http404("Permission denied")

    export_prereqs_ok, error_msg = _check_export_prerequisites()
    if not export_prereqs_ok:
        raise Http404(error_msg)

    wb = openpyxl.Workbook(write_only=True)
    ws_info = wb.create_sheet(_("Active accounts"))
    ws_info.append(_export_excel_accounts_active_get_header_info())

    date_format = "%d-%m-%Y"
    accounts = Account.objects.filter(is_active=True)

    for account in accounts:
        # Account subscription info
        latest_subscription = _get_latest_subscription(account)
        latest_pause = _get_current_or_upcoming_pause(latest_subscription)
        # Account classpass info
        latest_classpass = _get_latest_classpass(account)
        # Bank account
        bankaccount = account.bank_accounts.first() if account.bank_accounts.first() else ""

        # Active accounts list
        ws_info.append([
            "J" if account.is_active else "N", # Login gegevens versturen
            account.created_at.strftime(date_format), # Datum inschrijving
            _get_initials(account.first_name), # Voorletters
            account.first_name, # Voornaam
            "", # Tussenvoegsel
            account.last_name, # Achternaam
            account.date_of_birth.strftime(date_format) if account.date_of_birth else "", # Geboortedatum
            _map_costasiella_gender_to_sportbit_gender(account.gender), # Geboortedatum
            _strip_housenumber_from_address(account.address), # Straat
            _get_housenumber(account.address), # Huisnummer
            account.postcode, # Postcode
            account.city, # Woonplaats
            account.country, # Country
            account.email, # Email
            account.phone, # Telefoonnummer vast
            account.mobile, # Telefoonnummer mobiel
            account.emergency, # Noodnummer
            account.invoice_to_business.name if account.invoice_to_business else "", # Bedrijfsnaam
            account.invoice_to_business.tax_registration if account.invoice_to_business else "", # BTWnummer
            account.invoice_to_business.registration if account.invoice_to_business else "", # Extern relatienummer
            # IBAN
            bankaccount.number if bankaccount != "" and bankaccount.number != "None" else "",  # IBAN
            account.bank_accounts.first().bic if account.bank_accounts.first() else "", # BIC
            account.bank_accounts.first().holder if account.bank_accounts.first() else "", # Renkening houser
            account.bank_accounts.first().mandates.first().reference if account.bank_accounts.first() and account.bank_accounts.first().mandates.first() else "", # Mandaat ID
            "", # Blessure/Lichamelijke klachten
            "", # Startdatum blessure
            map_costasiella_subscription_id_to_sportbit_id(latest_subscription.organization_subscription.id) if latest_subscription else "", # Product nummer abonnment
            latest_subscription.date_start.strftime(date_format) if latest_subscription else "", # Start abonnement
            latest_subscription.date_end.strftime(date_format) if latest_subscription and latest_subscription.date_end else "", # Einde abonnement
            "", # Opzegreden
            "", # Verloopdatum contract termijn
            latest_subscription.get_credits_total(datetime.date.today()) if latest_subscription else "", # Resterende credits
            latest_pause.date_start.strftime(date_format) if latest_pause else "", # Start pauze
            latest_pause.date_end.strftime(date_format) if latest_pause else "", # Evt. Activatiedatum Gepauzeerd Termijn Abonnement
            latest_pause.description if latest_pause else "", # evt. Pauze reden
            "", # Kortings %
            "31-12-2025" if latest_subscription else "", # Abonnement reeds betaald tm
            "Incasso" if latest_subscription else "", # Betaalwijze abonnement
            map_costasiella_classpass_id_to_sportbit_id(
                latest_classpass.organization_classpass.id) if latest_classpass else "", # Product nummer rittenkaart
            latest_classpass.date_start.strftime(date_format) if latest_classpass else "",  # Start rittenkaart
            latest_classpass.date_end.strftime(
                date_format) if latest_classpass and latest_classpass.date_end else "",  # verloop datum rittenkaart
            latest_classpass.classes_remaining if latest_classpass else "",  # Openstaande ritten
            "", # Familie account
            "", # Vaste les
            "", # Notities klantenkaart lid
        ])

    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    filename = f"SportBitManager.xlsx"

    return FileResponse(buffer, as_attachment=True, filename=filename)

def _get_initials(first_name: str) -> str:
    if not first_name:
        return ""

    names = first_name.strip().replace("&", "").replace("  ", " ").split(" ")
    initials = []
    for name in names:
        print(name)
        initials.append(name[0].upper())

    return " ".join(initials)

def _get_housenumber(address: str) -> str:
    housenumber = ""
    if not address:
        return housenumber

    # Look for one or more digits in the string
    match = re.search(r'\d+[a-zA-Z]?', address)
    if match:
        housenumber = match.group()

    return housenumber

def _strip_housenumber_from_address(address: str) -> str:
    return_value = ""
    if address:
        return_value = re.sub(r'\d+[a-zA-Z]?', '', address).strip()
    return return_value

def _get_latest_subscription(account: Account) -> AccountSubscription:
    qs = AccountSubscription.objects.filter(
        Q(date_end__gte="2026-01-01") | Q(date_end__isnull=True),
        organization_subscription__archived=0,
        account=account,
    )

    return qs.first()

def _get_current_or_upcoming_pause(account_subscription):
    qs = AccountSubscriptionPause.objects.filter(
        Q(date_end__gte=datetime.date.today()),
        account_subscription=account_subscription
    )

    return qs.first()

def _get_latest_classpass(account: Account) -> AccountClasspass:
    qs = AccountClasspass.objects.filter(
        Q(date_end__gte="2026-01-01") | Q(date_end__isnull=True),
        classes_remaining__gt=0,
        account=account,
    )

    return qs.first()

def _map_costasiella_gender_to_sportbit_gender(gender):
    # dict keyed by costasiella gender options

    gender_map = {
        "F": "vrouw",
        "M": "man",
        "X": "X"
    }

    return gender_map.get(gender, "")

def map_costasiella_classpass_id_to_sportbit_id(organization_classpass_id: int):
    # dict keyed by costasiella classpass id

    classpasses_map = settings.SPORTBIT_MAP_CLASSPASSES

    return classpasses_map.get(organization_classpass_id, "")

def map_costasiella_subscription_id_to_sportbit_id(organization_subscription_id: int):
    # dict keyed by costasiella subscription id

    subscriptions_map = settings.SPORTBIT_MAP_SUBSCRIPTIONS

    return subscriptions_map.get(organization_subscription_id, "")

def _get_enrollments(account_subscription):
    sportbit_vaste_les = ""
    qs = ScheduleItemEnrollment.objects.filter(
        Q(date_end__gte=datetime.date.today()) | Q(date_end__isnull=True),
        account_subscription=account_subscription
    )

    if qs:
        for i, enrollment in enumerate(qs):
            sportbit_class = _map_costasiella_schedule_item_id_to_sportbit_id(enrollment.schedule_item_id)
            sportbit_vaste_les += str(sportbit_class)
            if i+1 < len(qs) and len(qs) > 1 and sportbit_class != "":
                sportbit_vaste_les += ","

    return sportbit_vaste_les

def _map_costasiella_schedule_item_id_to_sportbit_id(schedule_item_id: int):
    # dict keyed by costasiella schedule_item_id
    classes_map = settings.SPORTBIT_MAP_CLASSES

    return classes_map.get(schedule_item_id, "")