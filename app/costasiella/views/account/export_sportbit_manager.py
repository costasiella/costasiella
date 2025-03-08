import io

from django.db.models import Q
from django.http import Http404, FileResponse
from django.utils.translation import gettext as _
import openpyxl

from ...models import Account
from ...modules.graphql_jwt_tools import get_user_from_cookie
from ...modules.gql_tools import get_rid


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

    wb = openpyxl.Workbook(write_only=True)
    ws_info = wb.create_sheet(_("Active accounts"))
    ws_info.append(_export_excel_accounts_active_get_header_info())

    accounts = Account.objects.filter(is_active=True)

    for account in accounts:
        # Active accounts list
        ws_info.append([
            "J" if account.is_active else "N", # Login gegevens versturen
            account.created_at, # Datum inschrijving
            _get_initials(account.first_name), # Voorletters
            account.first_name, # Voornaam
            "", # Tussenvoegsel
            account.last_name, # Achternaam
            account.date_of_birth, # Geboortedatum
            account.gender, # Geboortedatum
            account.address, # Straat
            "", # Huisnummer
            account.postcode, # Postcode
            account.city, # Woonplaats
            account.country, # Country
            account.email, # Email
            account.phone, # Telefoonnummer vast
            account.mobile, # Telefoonnummer mobiel
            account.emergency, # Noodnummer
            account.invoice_to_business.name, # Bedrijfsnaam
            account.invoice_to_business.tax_registration, # BTWnummer
            account.invoice_to_business.registration, # Extern relatienummer
            # IBAN




            account.key_number
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
    names = first_name.split(" ")
    initials = []
    for name in names:
        initials.append(name[0].upper())

    return " ".join(initials)
