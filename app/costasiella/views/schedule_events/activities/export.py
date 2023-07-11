import io

from django.db.models import Q
from django.http import Http404, FileResponse
from django.utils.translation import gettext as _
import openpyxl

from ....models import ScheduleEvent, ScheduleItem, ScheduleItemAttendance
from ....modules.graphql_jwt_tools import get_user_from_cookie
from ....modules.gql_tools import get_rid


def export_excel_schedule_event_activities_attendance(request, schedule_event_node_id):
    """
    Export Schedule Event Activity Attendance
    """
    user = get_user_from_cookie(request)
    if not user.has_perm("costasiella.view_scheduleitemattendance"):
        raise Http404("Permission denied")

    rid = get_rid(schedule_event_node_id)
    schedule_event_id = rid.id
    schedule_event = ScheduleEvent.objects.get(id=schedule_event_id)

    # Create Workbook
    wb = openpyxl.Workbook(write_only=True)

    # Create sheets - One for each activity (schedule_item)
    schedule_items = ScheduleItem.objects.filter(schedule_event=schedule_event).order_by("date_start", "time_start")
    for schedule_item in schedule_items:
        sheet_title = schedule_item.name

        # Add sheet to Workbook
        ws = wb.create_sheet(sheet_title)

        # Add header to the sheet
        ws_header = [
            _('First name'),
            _('Last name'),
            _('Email'),
            _('Ticket'),
            _('Invoice'),
            _('Invoice Status'),
            _('To be paid (balance)'),
        ]
        ws.append(ws_header)

        # Fetch attendance for schedule_item
        schedule_item_attendances = ScheduleItemAttendance.objects.filter(
            ~Q(booking_status='CANCELLED'),
            Q(schedule_item_id=schedule_item.id),
            Q(date=schedule_item.date_start)
        )

        for schedule_item_attendance in schedule_item_attendances:
            # Schedule event ticket
            account_schedule_event_ticket = schedule_item_attendance.account_schedule_event_ticket
            schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket

            # Invoice
            finance_invoice_item = schedule_item_attendance.finance_invoice_item
            try:
                finance_invoice = finance_invoice_item.finance_invoice
                finance_invoice.invoice_number
            except AttributeError:
                finance_invoice = None


            # Add rows to sheet
            row = [
                schedule_item_attendance.account.first_name,
                schedule_item_attendance.account.last_name,
                schedule_item_attendance.account.email,
                schedule_event_ticket.name,
                finance_invoice.invoice_number if finance_invoice else "",
                finance_invoice.status if finance_invoice else "",
                finance_invoice.balance if finance_invoice else ""
            ]
            ws.append(row)


    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    filename = f"{schedule_event.name}_activities_attendance.xlsx"

    return FileResponse(buffer, as_attachment=True, filename=filename)
