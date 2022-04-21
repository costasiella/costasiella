import io

from django.db.models import Q
from django.http import Http404, FileResponse
from django.utils.translation import gettext as _
import openpyxl

from ...models import ScheduleItem, ScheduleItemAttendance
from ...modules.graphql_jwt_tools import get_user_from_cookie
from ...modules.gql_tools import get_rid


def export_excel_schedule_item_attendance_mailinglist(request, schedule_item_node_id, date, **kwargs):
    """
    Export Schedule item attendance mailinglist
    """
    user = get_user_from_cookie(request)
    if not user.has_perm('costasiella.view_scheduleitemattendance'):
        raise Http404("Permission denied")

    rid = get_rid(schedule_item_node_id)
    schedule_item_id = rid.id
    schedule_item = ScheduleItem.objects.get(id=schedule_item_id)

    wb = openpyxl.Workbook(write_only=True)
    ws_header = [
        _('First name'),
        _('Last name'),
        _('Email'),
    ]

    sheet_title = _('MailingList')
    ws = wb.create_sheet(sheet_title)
    ws.append(ws_header)

    schedule_item_attendances = ScheduleItemAttendance.objects.filter(
        ~Q(booking_status='CANCELLED'),
        Q(schedule_item_id=schedule_item_id),
        Q(date=date)
    )

    for schedule_item_attendance in schedule_item_attendances:
        account = schedule_item_attendance.account
        ws.append([
            account.first_name,
            account.last_name,
            account.email
        ])

    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    # Set some variables to format the export filename
    location = schedule_item.organization_location_room.organization_location.name
    classtype = schedule_item.organization_classtype.name
    starttime = str(schedule_item.time_start)

    filename = f"MailingList_{location}_{classtype}_{date}_{starttime}.xlsx"

    return FileResponse(buffer, as_attachment=True, filename=filename)
