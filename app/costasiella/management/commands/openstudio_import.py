import sys
import os
import datetime

import django.db.utils
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError, no_translations
from django.utils import timezone
from django.conf import settings
import costasiella.models as m
from costasiella.modules.model_helpers.schedule_event_ticket_schedule_item_helper import \
    ScheduleEventTicketScheduleItemHelper
from costasiella.dudes.sales_dude import SalesDude

import MySQLdb
from MySQLdb._exceptions import OperationalError
import MySQLdb.converters

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = 'Import from OpenStudio. Provide at least --db_name, --db_user and --db_password.'
        self.cursor = None  # Set later on from handle

        # Costasiella media root isn't used in import. Fields already know where to store media.
        # Can self.cs_media_root = Line below be removed?
        self.cs_media_root = settings.MEDIA_ROOT
        self.os_media_root = None

        # Fixed maps
        self.map_validity_units_cards_and_memberships = {
            'days': 'DAYS',
            'weeks': 'WEEKS',
            'months': 'MONTHS'
        }

        self.map_validity_units_subscriptions = {
            'week': 'WEEK',
            'month': 'MONTH'
        }

        self.map_attendance_types = {
            None: 'SUBSCRIPTION',
            1: 'CLASSPASS',  # Trial
            2: 'CLASSPASS',  # Drop in
            3: 'CLASSPASS',
            4: 'COMPLEMENTARY',
            5: 'REVIEW',
            6: 'RECONCILE_LATER'
        }

        self.map_booking_statuses = {
            'booked': 'BOOKED',
            'attending': 'ATTENDING',
            'cancelled': 'CANCELLED'
        }

        self.map_classes_otc_statuses = {
            "normal": "",
            "open": "OPEN",
            "cancelled": "CANCELLED"
        }

        self.map_classes_instructor_roles = {
            0: "",
            1: "SUB",
            2: "ASSISTANT",
            3: "KARMA"
        }

        self.map_invoices_product_types = {
            'membership': 'MEMBERSHIPS',
            'subscription': 'SUBSCRIPTIONS',
            'classcard': 'CLASSPASSES',
            'dropin': 'DROPINCLASSES',
            'trial': 'TRIALCLASSES',
            'wsp': 'EVENT_TICKETS',
            'shop': 'SHOP_SALES',
            'teacher_payments': 'INSTRUCTOR_PAYMENTS',
            'employee_expenses': 'EMPLOYEE_EXPENSES'
        }

        self.map_invoices_statuses = {
            'draft': 'DRAFT',
            'sent': 'SENT',
            'paid': 'PAID',
            'cancelled': 'CANCELLED'
        }

        self.map_customers_orders_statuses = {
            'received': 'RECEIVED',
            'awaiting_payment': 'AWAITING_PAYMENT',
            'paid': 'PAID',
            'processing': 'PAID',
            'delivered': 'DELIVERED',
            'cancelled': 'CANCELLED'
        }

        # Define dynamic maps
        self.accounting_costcenters_map = None
        self.accounting_glaccounts_map = None
        self.tax_rates_map = None
        self.payment_methods_map = None
        self.school_memberships_map = None
        self.school_classcards_map = None
        self.school_classcards_groups_map = None
        self.school_classcards_groups_classcards_map = None
        self.school_subscriptions_map = None
        self.school_subscriptions_groups_map = None
        self.school_subscriptions_groups_subscriptions_map = None
        self.school_subscriptions_price_map = None
        self.school_classtypes_map = None
        self.school_discovery_map = None
        self.school_languages_map = None
        self.school_levels_map = None
        self.school_shifts_map = None
        self.school_locations_map = None
        self.school_locations_rooms_map = None
        self.auth_user_map = None
        self.auth_user_business_map = None
        self.customers_classcards_map = None
        self.customers_subscriptions_map = None
        self.customers_subscriptions_alt_prices_map = None
        self.customers_subscriptions_blocks_map = None
        self.customers_subscriptions_pauses_map = None
        self.customers_notes_map = None
        self.customers_documents_map = None
        self.customers_payment_info_map = None
        self.customers_payment_info_mandates_map = None
        self.classes_map = None
        self.classes_attendance_map = None
        self.classes_reservation_map = None
        self.classes_otc_map = None
        self.classes_otc_mail_map = None
        self.classes_school_classcards_groups_map = None
        self.classes_school_subscriptions_groups_map = None
        self.classes_teachers_map = None
        self.shifts_map = None
        self.shifts_otc_map = None
        self.shifts_staff_map = None
        self.workshops_map = None
        self.workshops_activities_map = None
        self.workshops_products_map = None
        self.workshops_products_activities_map = None
        self.workshops_products_customers_map = None
        self.workshops_activities_customers_map = None
        self.announcements_map = None
        self.customers_profile_announcements_map = None
        self.invoices_groups_map = None
        self.invoices_groups_product_types_map = None
        self.invoices_map = None
        self.invoices_items_map = None
        self.invoices_payments_map = None
        self.invoices_mollie_payments_ids_map = None
        self.customers_orders_map = None
        self.customers_orders_items_map = None
        self.customers_orders_mollie_payment_ids_map = None
        self.payment_categories_map = None
        self.alternative_payments_map = None
        self.payment_batches_map = None
        self.payment_batches_exports_map = None
        self.payment_batches_items_map = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--db_name',
            type=str,
            required=True,
            help="OpenStudio database name"
        )
        parser.add_argument(
            '--db_user',
            type=str,
            required=True,
            help="OpenStudio database username"
        )
        parser.add_argument(
            '--db_password',
            type=str,
            required=True,
            help="OpenStudio database password for db_user"
        )
        parser.add_argument(
            '--db_host',
            type=str,
            default="localhost",
            help="OpenStudio database host (default: localhost)"
        )
        parser.add_argument(
            '--db_port',
            type=int,
            default=3306,
            help="OpenStudio database port (default: 3306)"
        )
        parser.add_argument(
            '--os_uploads_folder',
            type=str,
            default="",
            help="OpenStudio uploads folder (default: '')"
        )

    def _yes_or_no(self, question, exit_on_no=True):
        """
        A simple yes or no confirmation question
        :param question: String - question text
        :return: input asking a y/n question
        """
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            if exit_on_no:
                self.stdout.write("OpenStudio import stopped.")
                sys.exit(1)
            else:
                return False
        else:
            return self._yes_or_no("Uhhhh... please enter y or n")

    def _confirm_args(self, **options):
        """
        Confirm passed options
        :param options: parser options
        :return: result of _yes_or_no
        """
        self.stdout.write("")
        self.stdout.write("OpenStudio DB connection info:")
        self.stdout.write("-----")
        self.stdout.write("db: %s" % options['db_name'])
        self.stdout.write("user: %s" % options['db_user'])
        self.stdout.write("password: %s" % options['db_password'])
        self.stdout.write("host: %s" % options['db_host'])
        self.stdout.write("port: %s" % options['db_port'])
        self.stdout.write("-----")
        self.stdout.write("")
        self.stdout.write("-----")
        self.stdout.write("Media folders:")
        self.stdout.write("Costasiella: %s" % self.cs_media_root)
        self.stdout.write("OpenStudio: %s" % options['os_uploads_folder'])
        self.stdout.write("-----")
        self.stdout.write("")

        return self._yes_or_no("Test connection & start import using the settings above?")

    def _connect_to_db_and_set_cursor(self, host, user, password, db, port):
        """

        :return:
        """
        # Conversion mapping
        # https://mysqlclient.readthedocs.io/user_guide.html#some-examples
        # os_db_conv = {
        #     FIELD_TYPE.: int,
        #     FIELD_TYPE.LONG: int,
        #     FIELD_TYPE.VARCHAR: str,
        #     FIELD_TYPE.CHAR: str,
        #     FIELD_TYPE.FLOAT: float,
        #     FIELD_TYPE.DOUBLE: float,
        #     # FIELD_TYPE.DATE: datetime.date,
        #     # FIELD_TYPE.DATETIME: datetime.datetime,
        # }
        orig_conv = MySQLdb.converters.conversions
        conv_iter = iter(orig_conv)
        convert = dict(zip(conv_iter, [str,] * len(orig_conv.keys())))

        try:
            conn = MySQLdb.connect(
                host=host,
                user=user,
                passwd=password,
                db=db,
                port=port,
                charset="latin1",
                # conv=convert
            )
        except OperationalError as e:
            self.stdout.write("OpenStudio MySQL connection: " + self.style.ERROR("FAILED"))
            self.stdout.write("The following error message was received:")
            self.stdout.write(str(e))
            self.stdout.write("")
            self.stdout.write("Exiting...")
            sys.exit(1)

        return conn.cursor(MySQLdb.cursors.DictCursor)

    @no_translations
    def handle(self, *args, **options):
        """
        Main command function (options defined in add_arguments)
        :param args: command args
        :param options: command options
        :return:
        """
        options_confirmation = self._confirm_args(**options)
        if options_confirmation:
            # Set openstudio media folder (if any set)
            if options['os_uploads_folder']:
                self.os_media_root = options['os_uploads_folder']
            # Setup db connection
            self.stdout.write("")
            self.stdout.write("Testing OpenStudio MySQL connection...")
            self.cursor = self._connect_to_db_and_set_cursor(
                host=options['db_host'],
                user=options['db_user'],
                password=options['db_password'],
                db=options['db_name'],
                port=options['db_port']
            )
            self.stdout.write("OpenStudio MySQL connection: " + self.style.SUCCESS("SUCCESS"))
            self.stdout.write("Starting import...")

        if not self.cursor:
            self.stdout.write("Error setting up MySQL connection, exiting...")
            sys.exit(1)

        self._import()

        """
        Example code;
        #####
        for poll_id in options['poll_ids']:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))        
        """

    @staticmethod
    def _web2py_bool_to_python(w2p_bool):
        if w2p_bool == "T":
            return True
        else:
            return False

    def get_records_import_status_display(self, records_imported, records_total, raw=False):
        records_display = "%s/%s" % (records_imported, records_total)

        if not raw:
            if records_imported == records_total:
                records_display = self.style.SUCCESS(records_display)
            else:
                records_display = self.style.ERROR(records_display)

        return records_display

    def _import(self):
        """
        Main import function
        :param cursor: MySQLdb connection cursor
        :return:
        """
        self._import_os_sys_organization_to_organization()
        self.accounting_costcenters_map = self._import_accounting_costcenters()
        self.accounting_glaccounts_map = self._import_accounting_glaccounts()
        self.tax_rates_map = self._import_tax_rates()
        self.payment_methods_map = self._import_payment_methods()
        # self.school_memberships_map = self._import_school_memberships()
        self.school_classcards_map = self._import_school_classcards()
        self.school_classcards_groups_map = self._import_school_classcards_groups()
        self.school_classcards_groups_classcards_map = self._import_school_classcards_groups_classcards()
        self.school_subscriptions_map = self._import_school_subscriptions()
        self.school_subscriptions_groups_map = self._import_school_subscriptions_groups()
        self.school_subscriptions_groups_subscriptions_map = self._import_school_subscriptions_groups_subscriptions()
        self.school_subscriptions_price_map = self._import_school_subscriptions_price()
        self.school_classtypes_map = self._import_school_classtypes()
        self.school_discovery_map = self._import_school_discovery()
        self.school_languages_map = self._import_school_langauges()
        self.school_levels_map = self._import_school_levels()
        self.school_shifts_map = self._import_school_shifts()
        locations_import_result = self._import_school_locations()
        self.school_locations_map = locations_import_result['id_map_locations']
        self.school_locations_rooms_map = locations_import_result['id_map_rooms']
        auth_user_result = self._import_auth_user()
        self.auth_user_map = auth_user_result['id_map_auth_user']
        self.auth_user_business_map = self._import_auth_user_business()
        self.customers_classcards_map = self._import_customers_classcards()
        self.customers_subscriptions_map = self._import_customers_subscriptions()
        self.customers_subscriptions_alt_prices_map = self._import_customers_subscriptions_alt_prices()
        self.customers_subscriptions_blocks_map = self._import_customers_subscriptions_blocks()
        self.customers_subscriptions_pauses_map = self._import_customers_subscriptions_pauses()
        self.customers_notes_map = self._import_customers_notes()
        self.customers_documents_map = self._import_customers_documents()
        self.customers_payment_info_map = self._import_customers_payment_info()
        self.customers_payment_info_mandates_map = self._import_customers_payment_mandates()
        self.classes_map = self._import_classes()
        self.classes_attendance_map = self._import_classes_attendance()
        self.classes_reservation_map = self._import_classes_reservation()
        self.classes_otc_map = self._import_classes_otc()
        self.classes_otc_mail_map = self._import_classes_otc_mail()
        self.classes_school_classcards_groups_map = self._import_classes_school_classcards_groups()
        self.classes_school_subscriptions_groups_map = self._import_classes_school_subscriptions_groups()
        self.classes_teachers_map = self._import_classes_teachers()
        self.shifts_map = self._import_shifts()
        self.shifts_otc_map = self._import_shifts_otc()
        self.shifts_staff_map = self._import_shifs_staff()
        self.workshops_map = self._import_workshops()
        self.workshops_activities_map = self._import_workshops_activities()
        self.workshops_products_map = self._import_workshops_products()
        self.workshops_products_activities_map = self._import_workshops_products_activities()
        self.workshops_products_customers_map = self._import_workshops_products_customers()
        self.workshops_activities_customers_map = self._import_workshops_activities_customers()
        self.announcements_map = self._import_announcements()
        self.customers_profile_announcements_map = self._import_customers_profile_announcements()
        self.invoices_groups_map = self._import_invoices_groups()
        self.invoices_groups_product_types_map = self._import_invoices_groups_product_types()
        self.invoices_map = self._import_invoices()
        self.invoices_items_map = self._import_invoices_items()
        self.invoices_payments_map = self._import_invoices_payments()
        self.invoices_mollie_payments_ids_map = self._import_invoices_mollie_payment_ids()
        self.customers_orders_map = self._import_customers_orders()
        self.customers_orders_items_map = self._import_customers_orders_items()
        self.customers_orders_mollie_payment_ids_map = self._import_customers_orders_mollie_payment_ids()
        self.payment_categories_map = self._import_payment_categories()
        self.alternative_payments_map = self._import_alternative_payments()
        self.payment_batches_map = self._import_payment_batches()
        self.payment_batches_exports_map = self._import_payment_batches_exports()
        self.payment_batches_items_map = self._import_payment_batches_items()

        self._update_account_classpasses_remaining()

    def _import_os_sys_organization_to_organization(self):
        """
        Fetch the default organization and import it in Costasiella.
        Other organizations can't be imported at this time.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from sys_organizations WHERE DefaultOrganization = 'T'"
        self.cursor.execute(query)
        record = self.cursor.fetchone()

        if record:
            record = {k.lower(): v for k, v in record.items()}
            organization = m.Organization.objects.get(pk=100)
            organization.archived = self._web2py_bool_to_python(record['archived'])
            organization.name = record['name'] or ""
            organization.address = record['address'] or ""
            organization.phone = record['phone'] or ""
            organization.email = record['email'] or ""
            organization.registration = record['registration'] or ""
            organization.tax_registration = record['taxregistration'] or ""
            organization.save()

            self.stdout.write("Import default organization: " + self.style.SUCCESS("OK"))
            logger.info("Import default organization: OK")
        else:
            self.stdout.write("Import default organization: " + self.style.ERROR("No default organization found."))
            logger.error("Import default organization: No default organization found")

    def _import_accounting_glaccounts(self):
        """
        Fetch the glaccounts and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from accounting_glaccounts"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            finance_glaccount = m.FinanceGLAccount(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
                code=record['accountingcode']
            )
            finance_glaccount.save()
            records_imported += 1

            id_map[record['id']] = finance_glaccount

        log_message = "Import accounting_glaccounts: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_accounting_costcenters(self):
        """
        Fetch the costcenters and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from accounting_costcenters"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            finance_costcenter = m.FinanceCostCenter(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
                code=record['accountingcode']
            )
            finance_costcenter.save()
            records_imported += 1

            id_map[record['id']] = finance_costcenter

        log_message = "Import accounting_costcenters: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_tax_rates(self):
        """
        Fetch tax rates and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from tax_rates"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            finance_tax_rate = m.FinanceTaxRate(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
                percentage=record['percentage'],
                rate_type="IN",
                code=record['vatcodeid'] or ""
            )
            finance_tax_rate.save()
            records_imported += 1

            id_map[record['id']] = finance_tax_rate

        log_message = "Import tax_rates: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_payment_methods(self):
        """
        Fetch payment methods and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from payment_methods where SystemMethod = 'F'"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {
            1: m.FinancePaymentMethod.objects.get(id=101),
            2: m.FinancePaymentMethod.objects.get(id=102),
            3: m.FinancePaymentMethod.objects.get(id=103),
            100: m.FinancePaymentMethod.objects.get(id=100),
        }
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            finance_payment_method = m.FinancePaymentMethod(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
                code=record['accountingcode'] or ""
            )
            finance_payment_method.save()

            id_map[record['id']] = finance_payment_method
            records_imported += 1

        log_message = "Import payment methods: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_memberships(self):
        """
        Fetch school memberships and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_memberships"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            organization_membership = m.OrganizationMembership(
                archived=self._web2py_bool_to_python(record['archived']),
                display_public=self._web2py_bool_to_python(record['publicmembership']),
                display_shop=self._web2py_bool_to_python(record['publicmembership']),
                name=record['name'],
                description=record['description'] or "",
                price=record['price'] or 0,
                finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id'], None),
                validity=record['validity'],
                validity_unit=self.map_validity_units_cards_and_memberships.get(record['validityunit']),
                terms_and_conditions=record['terms'] or "",
                finance_glaccount=self.accounting_glaccounts_map.get(record['accounting_glaccounts_id'], None),
                finance_costcenter=self.accounting_costcenters_map.get(record['accounting_costcenters_id'], None)
            )
            organization_membership.save()
            records_imported += 1

            id_map[record['id']] = organization_membership

        log_message = "Import organization memberships: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_classcards(self):
        """
        Fetch school classcards and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_classcards"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            # Make all items lowercase
            record = {k.lower(): v for k, v in record.items()}

            organization_classpass = m.OrganizationClasspass(
                archived=self._web2py_bool_to_python(record['archived']),
                display_public=self._web2py_bool_to_python(record['publiccard']),
                display_shop=self._web2py_bool_to_python(record['publiccard']),
                trial_pass=self._web2py_bool_to_python(record['trialcard']),
                name=record['name'],
                description=record['description'] or "",
                price=record['price'],
                finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id'], None),
                validity=record['validity'] or 1,
                validity_unit=self.map_validity_units_cards_and_memberships.get(record['validityunit'], 'DAYS'),
                classes=record['classes'] or 0,
                unlimited=self._web2py_bool_to_python(record['unlimited']),
                # organization_membership=self.school_memberships_map.get(record['school_memberships_id'], None),
                quick_stats_amount=record['quickstatsamount'] or 0,
                finance_glaccount=self.accounting_glaccounts_map.get(record['accounting_glaccounts_id'], None),
                finance_costcenter=self.accounting_costcenters_map.get(record['accounting_costcenters_id'], None)
            )
            organization_classpass.save()
            records_imported += 1

            id_map[record['id']] = organization_classpass

        log_message = "Import organization classpasses: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_classcards_groups(self):
        """
        Fetch school classcards groups and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_classcards_groups"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            organization_classpass_group = m.OrganizationClasspassGroup(
                name=record['name'],
                description=record['description'] or "",
            )
            organization_classpass_group.save()
            records_imported += 1

            id_map[record['id']] = organization_classpass_group

        log_message = "Import organization classpass groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_classcards_groups_classcards(self):
        """
        Fetch school classcards groups classcards and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_classcards_groups_classcards"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            organization_classpass_group_classpass = m.OrganizationClasspassGroupClasspass(
                organization_classpass_group=self.school_classcards_groups_map.get(
                    record['school_classcards_groups_id']
                ),
                organization_classpass=self.school_classcards_map.get(record['school_classcards_id'])
            )
            organization_classpass_group_classpass.save()
            records_imported += 1

            id_map[record['id']] = organization_classpass_group_classpass

        log_message = "Import organization classpass groups classcards: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_subscriptions(self):
        """
        Fetch school subscriptions and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_subscriptions"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_subscription = m.OrganizationSubscription(
                archived=self._web2py_bool_to_python(record['archived']),
                display_public=self._web2py_bool_to_python(record['publicsubscription']),
                display_shop=self._web2py_bool_to_python(record['shopsubscription']),
                name=record['name'],
                description=record['description'] or "",
                sort_order=record['sortorder'],
                min_duration=record['minduration'],
                classes=record['classes'] or 0,
                subscription_unit=self.map_validity_units_subscriptions.get(record['subscriptionunit'], 'MONTH'),
                reconciliation_classes=record['reconciliationclasses'],
                credit_validity=record['creditvalidity'] or 1,
                unlimited=self._web2py_bool_to_python(record['unlimited']),
                terms_and_conditions=record['terms'] or "",
                registration_fee=record['registrationfee'] or 0,
                # organization_membership=self.school_memberships_map.get(record['school_memberships_id'], None),
                quick_stats_amount=record['quickstatsamount'] or 0,
            )
            organization_subscription.save()
            records_imported += 1

            id_map[record['id']] = organization_subscription

        log_message = "Import organization subscriptions: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_subscriptions_groups(self):
        """
        Fetch school subscriptions groups and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_subscriptions_groups"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_subscription_group = m.OrganizationSubscriptionGroup(
                name=record['name'],
                description=record['description'] or "",
            )
            organization_subscription_group.save()
            records_imported += 1

            id_map[record['id']] = organization_subscription_group

        log_message = "Import organization subscription groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_subscriptions_groups_subscriptions(self):
        """
        Fetch school subscriptions groups subscriptions and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_subscriptions_groups_subscriptions"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            organization_subscription_group_subscription = m.OrganizationSubscriptionGroupSubscription(
                organization_subscription_group=self.school_subscriptions_groups_map.get(
                    record['school_subscriptions_groups_id']
                ),
                organization_subscription=self.school_subscriptions_map.get(record['school_subscriptions_id'])
            )
            organization_subscription_group_subscription.save()
            records_imported += 1

            id_map[record['id']] = organization_subscription_group_subscription

        log_message = "Import organization subscription groups subscriptions: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_subscriptions_price(self):
        """
        Fetch school subscriptions prices and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_subscriptions_price"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}
            organization_subscription_price = m.OrganizationSubscriptionPrice(
                organization_subscription=self.school_subscriptions_map.get(record['school_subscriptions_id']),
                price=record['price'],
                finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id']),
                date_start=record['startdate'],
                date_end=record['enddate']
            )
            organization_subscription_price.save()
            records_imported += 1

            id_map[record['id']] = organization_subscription_price

        log_message = "Import organization subscription prices: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_classtypes(self):
        """
        Fetch school classtypes and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_classtypes"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            os_file = None
            if record.get('picture', None):
                os_file = os.path.join(self.os_media_root, record['picture'])

            organization_classtype = m.OrganizationClasstype(
                archived=self._web2py_bool_to_python(record['archived']),
                display_public=self._web2py_bool_to_python(record['allowapi']),
                name=record['name'],
                description=record['description'] or "",
                url_website=record['link'] or "",
            )
            try:
                with open(os_file, 'rb') as fh:
                    # Get the content of the file, we also need to close the content file
                    with ContentFile(fh.read()) as file_content:
                        # Set the media attribute of the article, but under an other path/filename
                        organization_classtype.image.save(record['picture'], file_content)
            except FileNotFoundError:
                logger.error("Could not locate classtype image: %s" % os_file)
            except TypeError:
                pass

            organization_classtype.save()

            records_imported += 1

            id_map[record['id']] = organization_classtype

        log_message = "Import organization classtypes: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_discovery(self):
        """
        Fetch school discovery and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_discovery"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_discovery = m.OrganizationDiscovery(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
            )
            organization_discovery.save()
            records_imported += 1

            id_map[record['id']] = organization_discovery

        log_message = "Import organization discovery: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_langauges(self):
        """
        Fetch school language and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_languages"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_language = m.OrganizationLanguage(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
            )
            organization_language.save()
            records_imported += 1

            id_map[record['id']] = organization_language

        log_message = "Import organization languages: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_levels(self):
        """
        Fetch school levels and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_levels"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_level = m.OrganizationLevel(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
            )
            organization_level.save()
            records_imported += 1

            id_map[record['id']] = organization_level

        log_message = "Import organization levels: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_shifts(self):
        """
        Fetch school shifts and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_shifts"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_shift = m.OrganizationShift(
                archived=self._web2py_bool_to_python(record['archived']),
                name=record['name'],
            )
            organization_shift.save()
            records_imported += 1

            id_map[record['id']] = organization_shift

        log_message = "Import organization shift: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_school_locations(self):
        """
        Fetch school locations and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_locations"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map_locations = {}
        id_map_rooms = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            organization_location = m.OrganizationLocation(
                archived=self._web2py_bool_to_python(record['archived']),
                display_public=self._web2py_bool_to_python(record['allowapi']),
                name=record['name'],
            )
            organization_location.save()
            id_map_locations[record['id']] = organization_location

            organization_location_room = m.OrganizationLocationRoom(
                organization_location=organization_location,
                archived=organization_location.archived,
                display_public=organization_location.display_public,
                name="Room 1"
            )
            organization_location_room.save()
            # os school_locations_id maps to cs room id
            id_map_rooms[record['id']] = organization_location_room

            records_imported += 1

        log_message = "Import organization locations: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return {
            'id_map_locations': id_map_locations,
            'id_map_rooms': id_map_rooms
        }

    def _import_auth_user(self):
        """
        Fetch auth users and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        # Import all users, as also business accounts might have cards or subscriptions attached to them
        query = "SELECT * FROM auth_user WHERE id > 1 AND merged='F' OR merged IS NULL OR merged=''"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map_auth_user = {}
        id_map_auth_user_teacher_profile = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            os_file = None
            if record.get('picture', None):
                os_file = os.path.join(self.os_media_root, record['picture'])

            try:
                account = m.Account(
                    is_active=not self._web2py_bool_to_python(record['trashed']),  # We need to invert this
                    customer=self._web2py_bool_to_python(record['customer']),
                    instructor=self._web2py_bool_to_python(record['teacher']),
                    employee=self._web2py_bool_to_python(record['teacher']),
                    first_name=record['first_name'],
                    last_name=record['last_name'],
                    full_name=record['full_name'] or "",
                    email=record['email'],
                    username=record['email'],
                    gender=record['gender'] or "",
                    date_of_birth=record['date_of_birth'] or "",
                    address=record['address'] or "",
                    postcode=record['postcode'] or "",
                    city=record['city'] or "",
                    country=record['country'] or "",
                    phone=record['phone'] or "",
                    mobile=record['mobile'] or "",
                    emergency=record['emergency'] or "",
                    key_number=record['keynr'] or "",
                    organization_discovery=self.school_discovery_map.get(record['school_discovery_id'], None),
                    organization_language=self.school_languages_map.get(record['school_languages_id'], None),
                    mollie_customer_id=record['mollie_customer_id'] or "",
                    created_at=record['created_on']
                )
                account.save()

                # Try to import picture
                try:
                    with open(os_file, 'rb') as fh:
                        # Get the content of the file, we also need to close the content file
                        with ContentFile(fh.read()) as file_content:
                            # Set the media attribute of the article, but under an other path/filename
                            account.image.save(record['picture'], file_content)
                except FileNotFoundError:
                    logger.error("Could not locate auth_user picture: %s" % os_file)
                except TypeError:
                    pass

                # Create allauth email
                account.create_allauth_email()

                # Create instructor profile
                self._import_auth_user_create_instructor_profile(account, record)

                # Create account bank account record
                account.create_bank_account()

                id_map_auth_user[record['id']] = account

                records_imported += 1
            except django.db.utils.IntegrityError as e:
                logger.error("Import auth_user error for user id: %s %s : %s" % (
                    record['id'],
                    record['email'],
                    e
                ))

        log_message = "Import auth_user: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return {
            'id_map_auth_user': id_map_auth_user,
        }

    def _import_auth_user_business(self):
        """
        Fetch business auth_user records and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from auth_user WHERE business = 'T' AND id > 1"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            business = m.Business(
                archived=self._web2py_bool_to_python(record['trashed']),
                b2b=True,
                supplier=False,
                vip=False,
                name=record['company'] or record['full_name'],
                address=record['address'] or "",
                postcode=record['postcode'] or "",
                city=record['city'] or "",
                country=record['country'] or "",
                phone=record['phone'] or "",
                phone_2=record['mobile'] or "",
                email_contact=record['email'] or "",
                email_billing=record['email'] or "",
                registration=record['company_registration'] or "",
                tax_registration=record['company_tax_registration'] or ""
            )
            business.save()
            records_imported += 1

            id_map[record['id']] = business

        log_message = "Import businesses: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_auth_user_create_instructor_profile(self, account, record):
        # Create instructor profile for account
        account_instructor_profile = account.create_instructor_profile()

        # Fill fields
        account_instructor_profile.classes = self._web2py_bool_to_python(record['teaches_classes'])
        account_instructor_profile.appointments = False
        account_instructor_profile.events = self._web2py_bool_to_python(record['teaches_workshops'])
        account_instructor_profile.role = record['teacher_role'] or ""
        account_instructor_profile.education = record['education'] or ""
        account_instructor_profile.bio = record['teacher_bio'] or ""
        account_instructor_profile.url_bio = record['teacher_bio_link'] or ""
        account_instructor_profile.url_website = record['teacher_website'] or ""

        account_instructor_profile.save()

    def _import_customers_classcards(self):
        """
        Fetch customer classcards and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from customers_classcards"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account_classpass = m.AccountClasspass(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    organization_classpass=self.school_classcards_map.get(record['school_classcards_id']),
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    note=record['note'] or "",
                    classes_remaining=0
                )
                account_classpass.save()
                records_imported += 1
                id_map[record['id']] = account_classpass

            except django.db.utils.IntegrityError as e:
                logger.error("Import customer classcard error for user id: %s classcard id: %s : %s" % (
                    record['auth_customer_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customer class cards: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_subscriptions(self):
        """
        Fetch customer subscriptins and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from customers_subscriptions"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account_subscription = m.AccountSubscription(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    organization_subscription=self.school_subscriptions_map.get(record['school_subscriptions_id'], None),
                    finance_payment_method=self.payment_methods_map.get(record['payment_methods_id'], None),
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    note=record['note'] or "",
                    registration_fee_paid=self._web2py_bool_to_python(record['registrationfeepaid'])
                )
                account_subscription.save()
                records_imported += 1
                id_map[record['id']] = account_subscription

            except django.db.utils.IntegrityError as e:
                logger.error("Import customer subscription error for user id: %s subscription id: %s : %s" % (
                    record['auth_customer_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customer subscriptions: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_subscriptions_alt_prices(self):
        """
        Fetch customer subscriptions alt prices and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM customers_subscriptions_alt_prices"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account_subscription_alt_price = m.AccountSubscriptionAltPrice(
                    account_subscription=self.customers_subscriptions_map.get(record['customers_subscriptions_id'],
                                                                              None),
                    subscription_year=record['subscriptionyear'],
                    subscription_month=record['subscriptionmonth'],
                    amount=record['amount'],
                    description=record['description'] or "",
                    note=record['note'] or ""
                )
                account_subscription_alt_price.save()
                records_imported += 1

                id_map[record['id']] = account_subscription_alt_price

            except django.db.utils.IntegrityError as e:
                logger.error("Import customer subscription alt price error subscription alt price id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import customer subscriptions alt prices: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_subscriptions_blocks(self):
        """
        Fetch customer subscriptions blocks and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM customers_subscriptions_blocked"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account_subscription_block = m.AccountSubscriptionBlock(
                    account_subscription=self.customers_subscriptions_map.get(record['customers_subscriptions_id'], None),
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    description=record['description'] or "",
                )
                account_subscription_block.save()
                records_imported += 1

                id_map[record['id']] = account_subscription_block
            except django.db.utils.IntegrityError as e:
                logger.error("Import customer subscription block error for subscription id: %s : %s: %s" % (
                    record['customers_subscriptions_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customer subscriptions block: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_subscriptions_pauses(self):
        """
        Fetch customer subscriptions pauses and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM customers_subscriptions_paused"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account_subscription_pause = m.AccountSubscriptionPause(
                    account_subscription=self.customers_subscriptions_map.get(record['customers_subscriptions_id'], None),
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    description=record['description'] or "",
                )
                account_subscription_pause.save()
                records_imported += 1

                id_map[record['id']] = account_subscription_pause
            except django.db.utils.IntegrityError as e:
                logger.error("Import customer subscription pause error for subscription id: %s : %s: %s" % (
                    record['customers_subscriptions_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customer subscriptions pause: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_notes(self):
        """
        Fetch customer notes and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from customers_notes"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        # Admin as default
        default_account = m.Account.objects.get(id=1)

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            note_type = "BACKOFFICE"
            if record['teachernote'] == "T":
                note_type = "INSTRUCTORS"

            try:
                account_note = m.AccountNote(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    note_by=self.auth_user_map.get(record['auth_user_id'], default_account),  # map to admin when not set
                    note_type=note_type,
                    note=record['note'] or "",
                    injury=self._web2py_bool_to_python(record['injury']),
                    processed=self._web2py_bool_to_python(record['processed']),
                )
                account_note.save()
                records_imported += 1

                id_map[record['id']] = account_note
            except django.db.utils.IntegrityError as e:
                logger.error("Import customer note error for user id: %s note id: %s : %s" % (
                    record['auth_customer_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customers notes: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_documents(self):
        """
        Fetch customers documents info and import it in Costasiella
        :return:
        """
        query = "SELECT * from customers_documents"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            os_file = None
            if record.get('documentfile', None):
                os_file = os.path.join(self.os_media_root, record['documentfile'])

            account = self.auth_user_map.get(record['auth_customer_id'], None)
            if not account:
                logger.error("Import customer document for user id: %s" % (
                    record['auth_customer_id'],
                ))
                continue

            account_document = m.AccountDocument(
                account = account,
                description=record['description'] or "",
            )
            try:
                with open(os_file, 'rb') as fh:
                    # Get the content of the file, we also need to close the content file
                    with ContentFile(fh.read()) as file_content:
                        # Set the media attribute of the article, but under an other path/filename
                        account_document.document.save(record['documentfile'], file_content)
            except FileNotFoundError:
                logger.error("Could not locate customer document: %s" % os_file)
                account_document.description = account_document.description = " (File not found)"
            except TypeError:
                pass

            account_document.save()

            records_imported += 1

            id_map[record['id']] = account_document

        log_message = "Import account documents: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_payment_info(self):
        """
        Fetch customers payment info and import it in Costasiella.
        :return: None
        """
        query = "SELECT * FROM customers_payment_info"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            account = self.auth_user_map.get(record['auth_customer_id'], None)
            if not account:
                logger.error("Import customer payment info error for user id: %s" % (
                    record['auth_customer_id'],
                ))
                continue

            account_bank_account = m.AccountBankAccount.objects.filter(account=account).first()
            account_bank_account.number = record['accountnumber'] or ""
            account_bank_account.holder = record['accountholder'] or ""
            account_bank_account.bic = record['bic'] or ""
            account_bank_account.save()

            id_map[record['id']] = account_bank_account

            records_imported += 1

        log_message = "Import customers payment info (bank accounts): "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_payment_mandates(self):
        """
        Fetch customers payment info mandates and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM customers_payment_info_mandates"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                content = ""
                if record['mandatetext']:
                    content = record['mandatetext'][:250]

                account_bank_account_mandate = m.AccountBankAccountMandate(
                    account_bank_account=self.customers_payment_info_map.get(record['customers_payment_info_id'], None),
                    reference=record['mandatereference'] or "",
                    content=content,
                    signature_date=record['mandatesignaturedate']
                )
                account_bank_account_mandate.save()
                records_imported += 1

                id_map[record['id']] = account_bank_account_mandate
            except django.db.utils.IntegrityError as e:
                logger.error("Import customer payment info mandate error for payment info id: %s note id: %s : %s" % (
                    record['customers_payment_info_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customers payment info (bank accounts) mandates: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes(self):
        """
        Fetch classes and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT cla.*, clm.* FROM classes cla LEFT JOIN classes_mail clm ON cla.id = clm.classes_id"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_item = m.ScheduleItem(
                    schedule_event=None,
                    schedule_item_type="CLASS",
                    frequency_type="WEEKLY",
                    frequency_interval=record['week_day'],
                    organization_location_room=self.school_locations_rooms_map.get(record['school_locations_id'], None),
                    organization_classtype=self.school_classtypes_map.get(record['school_classtypes_id'], None),
                    organization_level=self.school_levels_map.get(record['school_levels_id'], None),
                    spaces=record['maxstudents'],
                    walk_in_spaces=record['walkinspaces'] or 0,
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    time_start=str(record['starttime']),
                    time_end=str(record['endtime']),
                    display_public=self._web2py_bool_to_python(record['allowapi']),
                    info_mail_content=record['mailcontent'] or ""
                )
                schedule_item.save()
                records_imported += 1

                id_map[record['id']] = schedule_item
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_attendance(self):
        """
        Fetch classes attendance and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        import json

        query = "SELECT * FROM classes_attendance"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0

        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_item_attendance = m.ScheduleItemAttendance(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    account_classpass=self.customers_classcards_map.get(record['customers_classcards_id'], None),
                    account_subscription=self.customers_subscriptions_map.get(record['customers_subscriptions_id'],
                                                                              None),
                    finance_invoice_item=None,
                    # Set to True when account has membership at time of check-in
                    attendance_type=self.map_attendance_types.get(record['attendancetype'], None),
                    date=record['classdate'],
                    online_booking=self._web2py_bool_to_python(record['online_booking']),
                    booking_status=self.map_booking_statuses.get(record['bookingstatus'])
                )
                schedule_item_attendance.save()
                records_imported += 1

                id_map[record['id']] = schedule_item_attendance
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class attendance: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes attendance: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_reservation(self):
        """
        Fetch classes_reservation and import it into schedule_item_enrollments in Costasiella
        :return:
        """
        query = "SELECT * FROM classes_reservation where ResType='recurring'"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                date_end = None
                if record['enddate']:
                    date_end = record['enddate']

                schedule_item_enrollment = m.ScheduleItemEnrollment(
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    account_subscription=self.customers_subscriptions_map.get(record['customers_subscriptions_id']),
                    date_start=record['startdate'],
                    date_end=date_end,

                )
                schedule_item_enrollment.save()
                records_imported += 1

                id_map[record['id']] = schedule_item_enrollment
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class reservation id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes reservation: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_otc(self):
        """
        Fetch classes and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM classes_otc"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                startime = None
                endtime = None
                if record['starttime']:
                    startime = str(record['starttime'])
                if record['endtime']:
                    endtime = str(record['endtime'])

                schedule_item_weekly_otc = m.ScheduleItemWeeklyOTC(
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    date=record['classdate'],
                    status=self.map_classes_otc_statuses.get(record['status'], ""),
                    description=record['description'] or '',
                    account=self.auth_user_map.get(record['auth_teacher_id'], None),
                    role=self.map_classes_instructor_roles.get(record['teacher_role'], ""),
                    account_2=self.auth_user_map.get(record['auth_teacher_id2'], None),
                    role_2=self.map_classes_instructor_roles.get(record['teacher_role2'], ""),
                    organization_location_room=self.school_locations_rooms_map.get(record['school_locations_id'], None),
                    organization_classtype=self.school_classtypes_map.get(record['school_classtypes_id'], None),
                    time_start=startime,
                    time_end=endtime,
                    spaces=record['maxstudents'] or None,
                    walk_in_spaces=record['walkinspaces'] or None,
                    info_mail_content=""
                )
                schedule_item_weekly_otc.save()
                records_imported += 1

                id_map[record['id']] = schedule_item_weekly_otc
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class otc id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes otc: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_otc_mail(self):
        """
        Fetch classes otc mail and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM classes_otc_mail"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            qs = m.ScheduleItemWeeklyOTC.objects.filter(
                schedule_item=self.classes_map.get(record['classes_id'], None),
                date=record['classdate']
            )

            if qs.exists():
                schedule_item_weekly_otc = qs.first()
                schedule_item_weekly_otc.info_mail_content = record['mailcontent'] or ""
                schedule_item_weekly_otc.save()

                records_imported += 1

                id_map[record['id']] = schedule_item_weekly_otc
            else:
                # No need to throw a warning here. If there's no otc class, no need to import this record
                logger.info("No class OTC defined for classes_otc_mail id: %s" % (
                    record['id'],
                ))

        log_message = "Import classes otc mail: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_school_classcards_groups(self):
        """
        Fetch classes school classcards groups and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM classes_school_classcards_groups"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                siocg = m.ScheduleItemOrganizationClasspassGroup(
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    organization_classpass_group=self.school_classcards_groups_map.get(
                        record['school_classcards_groups_id'], None),
                    shop_book=self._web2py_bool_to_python(record['shopbook']),
                    attend=self._web2py_bool_to_python(record['attend'])
                )
                siocg.save()
                records_imported += 1

                id_map[record['id']] = siocg
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class school classcards group id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes school classcards groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_school_subscriptions_groups(self):
        """
        Fetch classes school classcards groups and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM classes_school_subscriptions_groups"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                siosg = m.ScheduleItemOrganizationSubscriptionGroup(
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    organization_subscription_group=self.school_subscriptions_groups_map.get(
                        record['school_subscriptions_groups_id'], None),
                    enroll=self._web2py_bool_to_python(record['enroll']),
                    shop_book=self._web2py_bool_to_python(record['shopbook']),
                    attend=self._web2py_bool_to_python(record['attend'])
                )
                siosg.save()
                records_imported += 1

                id_map[record['id']] = siosg
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class school subscriptions group id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes school subscriptions groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_classes_teachers(self):
        """
        Fetch classes teachers and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM classes_teachers"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_item_account = m.ScheduleItemAccount(
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    account=self.auth_user_map.get(record['auth_teacher_id'], None),
                    role=self.map_classes_instructor_roles.get(record['teacher_role'], ""),
                    account_2=self.auth_user_map.get(record['auth_teacher_id2'], None),
                    role_2=self.map_classes_instructor_roles.get(record['teacher_role2'], ''),
                    date_start=record['startdate'],
                    date_end=record['enddate']
                )
                schedule_item_account.save()
                records_imported += 1

                id_map[record['id']] = schedule_item_account
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class teacher id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import classes teachers: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_shifts(self):
        """
        Fetch shifts and import them in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from shifts"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_item = m.ScheduleItem(
                    schedule_event=None,
                    schedule_item_type="SHIFT",
                    frequency_type="WEEKLY",
                    frequency_interval=record['week_day'],
                    organization_location_room=self.school_locations_rooms_map.get(record['school_locations_id'], None),
                    organization_shift=self.school_shifts_map.get(record['school_shifts_id'], None),
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    time_start=str(record['starttime']),
                    time_end=str(record['endtime']),
                )
                schedule_item.save()
                records_imported += 1

                id_map[record['id']] = schedule_item
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for shift id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import shifts: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_shifts_otc(self):
        """
        Fetch shifts otc and import them in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM shifts_otc"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                startime = None
                endtime = None
                if record['starttime']:
                    startime = str(record['starttime'])
                if record['endtime']:
                    endtime = str(record['endtime'])

                schedule_item_weekly_otc = m.ScheduleItemWeeklyOTC(
                    schedule_item=self.classes_map.get(record['shifts_id'], None),
                    date=record['shiftdate'],
                    status=self.map_classes_otc_statuses.get(record['status'], ""),
                    description=record['description'] or '',
                    account=self.auth_user_map.get(record['auth_employee_id'], None),
                    account_2=self.auth_user_map.get(record['auth_employee_id2'], None),
                    organization_location_room=self.school_locations_rooms_map.get(record['school_locations_id'], None),
                    organization_shift=self.school_shifts_map.get(record['school_shifts_id'], None),
                    time_start=startime,
                    time_end=endtime,
                )
                schedule_item_weekly_otc.save()
                records_imported += 1

                id_map[record['id']] = schedule_item_weekly_otc
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for class otc id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import shifts otc: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_shifs_staff(self):
        """
        Fetch shifts staff and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * FROM shifts_staff"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_item_account = m.ScheduleItemAccount(
                    schedule_item=self.shifts_map.get(record['shifts_id'], None),
                    account=self.auth_user_map.get(record['auth_employee_id'], None),
                    account_2=self.auth_user_map.get(record['auth_employee_id2'], None),
                    date_start=record['startdate'],
                    date_end=record['enddate']
                )
                schedule_item_account.save()
                records_imported += 1

                id_map[record['id']] = schedule_item_account
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for shift staff id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import shift staff: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_subscriptions_credits(self):
        """
        Fetch customers subscriptions credits and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        today = timezone.now().date()

        query = """
SELECT 
	customers_subscriptions_id, 
	( SELECT CEILING(SUM(mutationamount)) 
		FROM customers_subscriptions_credits csc_added 
		WHERE customers_subscriptions_id = csc.customers_subscriptions_id 
		AND MutationType = "add") as credits_added,
	( SELECT FLOOR(SUM(mutationamount)) 
		FROM customers_subscriptions_credits csc_added 
		WHERE customers_subscriptions_id = csc.customers_subscriptions_id 
		AND MutationType = "sub") as credits_used,
	( SELECT credits_added - credits_used) as credits_remaining
FROM customers_subscriptions_credits csc 
GROUP BY customers_subscriptions_id 
        """
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            if record['credits_remaining'] > 0:
                ## Calculate expiration
                account_subscription = account_subscription=self.customers_subscriptions_map.get(
                    record['customers_subscriptions_id'], None
                )
                if not account_subscription:
                    logger.error("Import error for customers subscriptions credits (subscription id): %s" % (
                        record['customers_subscriptions_id']
                    ))
                    continue

                credit_validity = account_subscription.organization_subscription.credit_validity
                credit_expiration = today + datetime.timedelta(days=credit_validity)

                for i in range(0, record['credits_remaining']):
                    try:
                        # With expiration defined by organization subscription
                        account_subscription_credit = m.AccountSubscriptionCredit(
                            account_subscription=account_subscription,
                            expiration=credit_expiration,
                            description="Imported from OpenStudio"
                        )
                        account_subscription_credit.save()
                        records_imported += 1

                    except django.db.utils.IntegrityError as e:
                        logger.error("Import error for customers subscriptions credits id: %s: %s" % (
                            record['id'],
                            e
                        ))

        log_message = "Import customers subscriptions credits: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        # No id map is generated, as the credit schema in Costasiella differs from the one in OpenStudio
        # There can be no 1:1 mapping of credits.

        return None

    def _import_workshop_picture(self, schedule_event, os_picture_file_name, sort_order):
        """
        Save openstudio workshop picture as schedule_event_media
        :param schedule_event:
        :param picture:
        :return:
        """
        os_file = os.path.join(self.os_media_root, os_picture_file_name)

        try:
            with open(os_file, 'rb') as fh:
                # Get the content of the file, we also need to close the content file
                with ContentFile(fh.read()) as file_content:
                    # Set the media attribute of the article, but under an other path/filename
                    schedule_event_media = m.ScheduleEventMedia(
                        schedule_event=schedule_event,
                        sort_order=sort_order,
                        description="OpenStudio image %s" % str(sort_order + 1),
                    )
                    schedule_event_media.save()
                    schedule_event_media.image.save(os_picture_file_name, file_content)
                    schedule_event_media.save()

        except FileNotFoundError:
            logger.error("Could not locate schedule event image: %s" % os_file)
        except TypeError as e:
            logger.error("Caught a type error when importing schedule event image: %s : %s" % (os_file, e))

    def _import_workshops(self):
        """
        Fetch workshops and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = """
SELECT * FROM workshops w
LEFT JOIN workshops_mail wm ON wm.workshops_id = w.id
"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                tagline = ""
                if record['tagline']:
                    tagline = record['tagline'][:254]

                schedule_event = m.ScheduleEvent(
                    archived=self._web2py_bool_to_python(record['archived']),
                    display_public=self._web2py_bool_to_python(record['publicworkshop']),
                    display_shop=self._web2py_bool_to_python(record['publicworkshop']),
                    auto_send_info_mail=self._web2py_bool_to_python(record['autosendinfomail']),
                    organization_location=self.school_locations_map.get(record['school_locations_id']),
                    name=record['name'],
                    tagline=tagline,
                    preview=record['preview'] or "",
                    description=record['description'] or "",
                    organization_level=self.school_levels_map.get(record['school_levels_id']),
                    instructor=self.auth_user_map.get(record['auth_teacher_id']),
                    instructor_2=self.auth_user_map.get(record['auth_teacher_id2']),
                    date_start=record['startdate'],
                    date_end=record['enddate'],
                    time_start=str(record['starttime']) if record['starttime'] else None,
                    time_end=str(record['endtime']) if record['endtime'] else None,
                    info_mail_content=record['mailcontent'] or ""
                )
                schedule_event.save()
                records_imported += 1

                id_map[record['id']] = schedule_event

                # Import images
                if record.get('picture', None):
                    self._import_workshop_picture(schedule_event, record['picture'], 0)
                if record.get('picture_2', None):
                    self._import_workshop_picture(schedule_event, record['picture_2'], 1)
                if record.get('picture_3', None):
                    self._import_workshop_picture(schedule_event, record['picture_3'], 2)
                if record.get('picture_4', None):
                    self._import_workshop_picture(schedule_event, record['picture_4'], 3)
                if record.get('picture_5', None):
                    self._import_workshop_picture(schedule_event, record['picture_5'], 4)

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for workshop id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import workshops: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_workshops_activities(self):
        """
        Fetch workshops activities and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM workshops_activities"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_item = m.ScheduleItem(
                    schedule_event=self.workshops_map.get(record['workshops_id']),
                    schedule_item_type='EVENT_ACTIVITY',
                    frequency_type='SPECIFIC',
                    frequency_interval=0,
                    organization_location_room=self.school_locations_rooms_map.get(record['school_locations_id']),
                    name=record['activity'],
                    spaces=record['spaces'],
                    date_start=record['activitydate'],
                    time_start=str(record['starttime']),
                    time_end=str(record['endtime']),
                    display_public=True,
                    account=self.auth_user_map.get(record['auth_teacher_id']),
                    account_2=self.auth_user_map.get(record['auth_teacher_id2'], None)
                )
                schedule_item.save()
                records_imported += 1

                id_map[record['id']] = schedule_item

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for workshop activity id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import workshops activities: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_workshops_products(self):
        """
        Fetch workshops products and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM workshops_products"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        helper = ScheduleEventTicketScheduleItemHelper()
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                schedule_event_ticket = m.ScheduleEventTicket(
                    schedule_event=self.workshops_map.get(record['workshops_id']),
                    full_event=self._web2py_bool_to_python(record['fullworkshop']),
                    deletable=self._web2py_bool_to_python(record['deletable']),
                    display_public=self._web2py_bool_to_python(record['publicproduct']),
                    name=record['name'],
                    description=record['description'] or "",
                    price=record['price'] or 0,
                    finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id']),
                    finance_glaccount=self.accounting_glaccounts_map.get(record['accounting_glaccounts_id'], None),
                    finance_costcenter=self.accounting_costcenters_map.get(record['accounting_costcenters_id'], None)
                )
                schedule_event_ticket.save()
                # Add all schedule items for this event to this ticket
                helper.add_schedule_items_to_ticket(schedule_event_ticket)
                # Increase counter
                records_imported += 1

                id_map[record['id']] = schedule_event_ticket

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for workshop product id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import workshops products: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_workshops_products_activities(self):
        """
        Fetch workshops products activities and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM workshops_products_activities"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            # Find corresponding record in Costasiella
            qs = m.ScheduleEventTicketScheduleItem.objects.filter(
                schedule_event_ticket=self.workshops_products_map.get(record['workshops_products_id'], None),
                schedule_item=self.workshops_activities_map.get(record['workshops_activities_id'], None)
            )
            if qs.exists():
                # OpenStudio has a record in case it's included
                schedule_event_ticket_schedule_item = qs.first()
                schedule_event_ticket_schedule_item.included = True
                schedule_event_ticket_schedule_item.save()

                records_imported += 1
                id_map[record['id']] = schedule_event_ticket_schedule_item

        log_message = "Import workshops products activities: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_workshops_products_customers(self):
        """
        Fetch workshops products customers and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM workshops_products_customers"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        sales_dude = SalesDude()
        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account_schedule_event_ticket = m.AccountScheduleEventTicket(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    schedule_event_ticket=self.workshops_products_map.get(record['workshops_products_id'], None),
                    cancelled=self._web2py_bool_to_python(record['cancelled']),
                    payment_confirmation=self._web2py_bool_to_python(record['paymentconfirmation']),
                    info_mail_sent=self._web2py_bool_to_python(record['workshopinfo'])
                )
                account_schedule_event_ticket.save()
                # Add attendance items for customer
                sales_dude._sell_schedule_event_ticket_add_attendance(
                    account_schedule_event_ticket=account_schedule_event_ticket,
                    finance_invoice_item=None
                )

                # Increase counter
                records_imported += 1

                id_map[record['id']] = account_schedule_event_ticket

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for workshop product customer id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import workshops product customers: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_workshops_activities_customers(self):
        """
        Fetch workshops activities customers and import it in Costasiella.
        Set status to "ATTENDING" when a matching record is found
        :return: None
        """
        query = """SELECT * FROM workshops_activities_customers"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            qs = m.ScheduleItemAttendance.objects.filter(
                account=self.auth_user_map.get(record['auth_customer_id'], None),
                schedule_item=self.workshops_activities_map.get(record['workshops_activities_id'], None)
            )

            if qs.exists():
                schedule_item_attendance = qs.first()
                schedule_item_attendance.booking_status = 'ATTENDING'
                schedule_item_attendance.save()

                # Increase counter
                records_imported += 1

                id_map[record['id']] = schedule_item_attendance
            else:
                logger.error("Import error for workshop activities customer id: %s" % (
                    record['id'],
                ))

        log_message = "Import workshops activities customers: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_announcements(self):
        """
        Fetch announcements and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM announcements"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                date_end = datetime.date(2999, 12, 31)
                if record['enddate']:
                    date_end = record['enddate']

                organization_announcement = m.OrganizationAnnouncement(
                    display_public=self._web2py_bool_to_python(record['visible']),
                    display_shop=False,
                    display_backend=True,
                    title=record['title'],
                    content=record['note'],
                    date_start=record['startdate'],
                    date_end=date_end,
                    priority=record['priority']
                )
                organization_announcement.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = organization_announcement

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for announcement id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import announcements: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_profile_announcements(self):
        """
        Fetch customer profile announcements and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM customers_profile_announcements"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                priority = 200
                if record['sticky'] == 'T':
                    priority = 100

                date_end = datetime.date(2999, 12, 31)
                if record['enddate']:
                    date_end = record['enddate']

                organization_announcement = m.OrganizationAnnouncement(
                    display_public=self._web2py_bool_to_python(record['publicannouncement']),
                    display_shop=True,
                    display_backend=False,
                    title=record['title'],
                    content=record['announcement'],
                    date_start=record['startdate'],
                    date_end=date_end,
                    priority=priority
                )
                organization_announcement.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = organization_announcement

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for customer profile announcement id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import customer profile announcements: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_invoices_groups(self):
        """
        Fetch invoices groups and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        # Don't import default group
        query = "SELECT * FROM invoices_groups"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        # Add default group
        id_map[100] = m.FinanceInvoiceGroup.objects.get(id=100)

        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            if record['id'] == 100:
                finance_invoice_group = id_map[100]
                finance_invoice_group.archived = self._web2py_bool_to_python(record['archived'])
                finance_invoice_group.display_public = self._web2py_bool_to_python(record['publicgroup'])
                finance_invoice_group.name = record['name']
                finance_invoice_group.next_id = record['nextid']
                finance_invoice_group.due_after_days = record['duedays']
                finance_invoice_group.prefix = record['invoiceprefix'] or ""
                finance_invoice_group.prefix_year = self._web2py_bool_to_python(record['prefixyear'])
                finance_invoice_group.auto_reset_prefix_year = \
                    self._web2py_bool_to_python(record['autoresetprefixyear'])
                finance_invoice_group.terms = record['terms'] or ""
                finance_invoice_group.footer = record['footer'] or ""
                finance_invoice_group.code = record['journalid'] or ""
                finance_invoice_group.save()
                records_imported += 1

                logger.info("Imported default finance invoice group info")
            else:
                # Import non-default group
                try:
                    finance_invoice_group = m.FinanceInvoiceGroup(
                        archived=self._web2py_bool_to_python(record['archived']),
                        display_public=self._web2py_bool_to_python(record['publicgroup']),
                        name=record['name'],
                        next_id=record['nextid'],
                        due_after_days=record['duedays'],
                        prefix=record['invoiceprefix'] or "",
                        prefix_year=self._web2py_bool_to_python(record['prefixyear']),
                        auto_reset_prefix_year=self._web2py_bool_to_python(record['autoresetprefixyear']),
                        terms=record['terms'] or "",
                        footer=record['footer'] or "",
                        code=record['journalid'] or ""
                    )
                    finance_invoice_group.save()
                    records_imported += 1

                    id_map[record['id']] = finance_invoice_group
                except django.db.utils.IntegrityError as e:
                    logger.error("Import error for invoice group: %s: %s" % (
                        record['id'],
                        e
                    ))

        log_message = "Import invoice groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_invoices_groups_product_types(self):
        """
        Fetch invoices groups prouct types and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        # Don't import default group
        query = "SELECT * FROM invoices_groups_product_types"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_invoice_group_default = m.FinanceInvoiceGroupDefault.objects.filter(
                    item_type=self.map_invoices_product_types.get(record['producttype'])
                ).first()
                finance_invoice_group_default.finance_invoice_group = self.invoices_groups_map.get(
                    record['invoices_groups_id'], 100
                )  # Set to default (100) if the group is not found
                finance_invoice_group_default.save()
                records_imported += 1

                id_map[record['id']] = finance_invoice_group_default
            except AttributeError as e:
                logger.error("Import error for invoice group default: %s: %s" % (
                    record['id'],
                    e
                ))
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for invoice group default: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import invoice group defaults: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_invoices(self):
        """
        Fetch invoices and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = """
SELECT * FROM invoices i
LEFT JOIN invoices_customers ic  ON ic.invoices_id = i.id
LEFT JOIN invoices_amounts ia ON ia.invoices_id = i.id
ORDER BY i.id
"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                try:
                    credit_invoice_for = id_map.get(record['credit_invoice_for'].id)
                except AttributeError:
                    credit_invoice_for = None

                summary = ""
                if record['description']:
                    summary = record['description'][:254]

                account = self.auth_user_map.get(record['auth_customer_id'], None)
                finance_invoice = m.FinanceInvoice(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    finance_invoice_group=self.invoices_groups_map.get(record['invoices_groups_id'], None),
                    finance_payment_method=self.payment_methods_map.get(record['payment_methods_id'], None),
                    instructor_payment=self._web2py_bool_to_python(record['teacherpayment']),
                    employee_claim=self._web2py_bool_to_python(record['employeeclaim']),
                    status=self.map_invoices_statuses.get(record['status']),
                    summary=summary,
                    invoice_number=record['invoiceid'],
                    date_sent=record['datecreated'],
                    date_due=record['datedue'],
                    terms=record['terms'] or "",
                    footer=record['footer'] or "",
                    note=record['note'] or "",
                    subtotal=record['totalprice'],
                    tax=record['vat'],
                    total=record['totalpricevat'],
                    paid=record['paid'],
                    balance=record['balance'],
                    credit_invoice_for=credit_invoice_for
                )
                finance_invoice.save()

                finance_invoice.invoice_number = record['invoiceid']
                finance_invoice.save()
                records_imported += 1

                id_map[record['id']] = finance_invoice
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance invoice: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import finance invoices: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_invoices_items(self):
        """
        Fetch customers orders and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = """
SELECT * FROM invoices_items ii
LEFT JOIN invoices_items_workshops_products_customers iiwpc ON iiwpc.invoices_items_id = ii.id
LEFT JOIN invoices_items_classes_attendance iica ON iica.invoices_items_id = ii.id
LEFT JOIN invoices_items_customers_classcards iicc ON iicc.invoices_items_id = ii.id
LEFT JOIN invoices_items_customers_subscriptions iics ON iics.invoices_items_id = ii.id
LEFT JOIN invoices i ON ii.invoices_id = i.id
    """
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_invoice_item = m.FinanceInvoiceItem(
                    finance_invoice=self.invoices_map.get(record['invoices_id'], None),
                    account_schedule_event_ticket=self.workshops_products_customers_map.get(
                        record['workshops_products_customers_id'], None
                    ),
                    account_classpass=self.customers_classcards_map.get(
                        record['customers_classcards_id'], None
                    ),
                    account_subscription=self.customers_subscriptions_map.get(
                        record['customers_subscriptions_id'], None
                    ),
                    subscription_year=record['subscriptionyear'],
                    subscription_month=record['subscriptionmonth'],
                    line_number=record['sorting'],
                    product_name=record['productname'],
                    description=record['description'] or "",
                    quantity=record['quantity'],
                    price=record['price'],
                    finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id']),
                    finance_glaccount=self.accounting_glaccounts_map.get(record['accounting_glaccounts_id'], None),
                    finance_costcenter=self.accounting_costcenters_map.get(record['accounting_costcenters_id'], None)
                )
                finance_invoice_item.save()

                # This invoice item was linked to a classes_attendance record. There is no 1:1 equivalent in
                # Costasiella as there are no prices for a class but passes are used.
                # We can link the invoice item to an attendance record though.
                if record['classes_attendance_id']:
                    schedule_item_attendance = self.classes_attendance_map.get(
                        record['classes_attendance_id'],
                        None
                    )
                    if schedule_item_attendance:
                        schedule_item_attendance.finance_invoice_item = finance_invoice_item
                        schedule_item_attendance.save()

                records_imported += 1

                id_map[record['id']] = finance_invoice_item
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance invoice item: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import finance invoices items: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_invoices_payments(self):
        """
        Fetch invoice payments and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM invoices_payments"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_invoice_payment = m.FinanceInvoicePayment(
                    finance_invoice=self.invoices_map.get(record['invoices_id'], None),
                    date=record['paymentdate'],
                    amount=record['amount'] or 0,
                    finance_payment_method=self.payment_methods_map.get(record['payment_methods_id'], None),
                    note=record['note'] or "",
                    online_payment_id=record['mollie_payment_id'],
                    online_refund_id=record['mollie_refund_id'],
                    online_chargeback_id=record['mollie_chargeback_id'],
                )
                finance_invoice_payment.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = finance_invoice_payment

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for invoice payments id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import invoice payments: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_invoices_mollie_payment_ids(self):
        """
        Fetch records from invoices mollie payment ids and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM invoices_mollie_payment_ids"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                integration_log_mollie = m.IntegrationLogMollie(
                     log_source='INVOICE_PAY',
                     mollie_payment_id=record['mollie_payment_id'],
                     recurring_type=record['recurringtype'].upper() if record['recurringtype'] else None,
                     webhook_url=record['webhookurl'],
                     finance_invoice=self.invoices_map.get(record['invoices_id'], None)
                )
                integration_log_mollie.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = integration_log_mollie

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for invoices mollie payment id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import invoice mollie payments: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_orders(self):
        """
        Fetch customers orders and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = """
SELECT * FROM customers_orders co
LEFT JOIN customers_orders_amounts coa ON coa.customers_orders_id = co.id
LEFT JOIN invoices_customers_orders ico ON ico.customers_orders_id = co.id
"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_order = m.FinanceOrder(
                    finance_invoice=self.invoices_map.get(record['invoices_id'], None),
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    status=self.map_customers_orders_statuses.get(record['status'], None),
                    message=record['customernote'] or '',
                    subtotal=record['totalprice'] or 0,
                    tax=record['vat'] or 0,
                    total=record['totalpricevat'] or 0,
                    created_at=record['datecreated']
                )
                finance_order.save()
                records_imported += 1

                id_map[record['id']] = finance_order
            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance order: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import finance order id: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_orders_items(self):
        """
        Fetch customers orders items and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = """
SELECT * FROM customers_orders_items ii
    """
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_order_item = m.FinanceOrderItem(
                    finance_order=self.customers_orders_map.get(record['customers_orders_id'], None),
                    schedule_event_ticket=self.workshops_products_map.get(record['workshops_products_id'], None),
                    organization_subscription=self.school_subscriptions_map.get(record['school_subscriptions_id'],
                                                                                None),
                    organization_classpass=self.school_classcards_map.get(record['school_classcards_id'], None),
                    attendance_type=self.map_attendance_types.get(record['attendancetype'], None),
                    attendance_date=record['classdate'],
                    schedule_item=self.classes_map.get(record['classes_id'], None),
                    product_name=record['productname'],
                    description=record['description'] or '',
                    quantity=record['quantity'],
                    price=record['price'],
                    finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id']),
                    finance_glaccount=self.accounting_glaccounts_map.get(record['accounting_glaccounts_id'], None),
                    finance_costcenter=self.accounting_costcenters_map.get(record['accounting_costcenters_id'], None)
                )
                finance_order_item.save()
                records_imported += 1
                id_map[record['id']] = finance_order_item

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for customer order item: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import customer order items: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_customers_orders_mollie_payment_ids(self):
        """
        Fetch records from customers orders mollie payment ids and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM customers_orders_mollie_payment_ids"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                integration_log_mollie = m.IntegrationLogMollie(
                     log_source='ORDER_PAY',
                     mollie_payment_id=record['mollie_payment_id'],
                     recurring_type=record['recurringtype'].upper() if record['recurringtype'] else None,
                     webhook_url=record['webhookurl'],
                     finance_order=self.customers_orders_map.get(record['customers_orders_id'], None)
                )
                integration_log_mollie.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = integration_log_mollie

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for customers orders mollie payment id: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import customers orders mollie payments: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_payment_categories(self):
        """
        Fetch records from payment categories and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM payment_categories"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_payment_batch_category = m.FinancePaymentBatchCategory(
                    archived=self._web2py_bool_to_python(record['archived']),
                    name=record['name'],
                    batch_category_type='COLLECTION' if record['categorytype'] == 0 else 'PAYMENT',
                    description=""
                )
                finance_payment_batch_category.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = finance_payment_batch_category

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance payment batch category: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import payment batch categories: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_alternative_payments(self):
        """
        Fetch records from alternativepayments and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM alternativepayments"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                description = record['description'] or ''

                account_finance_payment_batch_category_item = m.AccountFinancePaymentBatchCategoryItem(
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    finance_payment_batch_category=self.payment_categories_map.get(
                        record['payment_categories_id'], None
                    ),
                    year=record['paymentyear'],
                    month=record['paymentmonth'],
                    amount=record['amount'],
                    description=description[0:255]
                )
                account_finance_payment_batch_category_item.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = account_finance_payment_batch_category_item

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for alternativepayment: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import alternativepayments: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_payment_batches(self):
        """
        Fetch records from payment batches and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM payment_batches"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                status = record['status'] or "AWAITING_APPROVAL"
                if status:
                    status = status.upper()

                finance_payment_batch = m.FinancePaymentBatch(
                    name=record['name'],
                    batch_type=record['batchtype'].upper(),
                    finance_payment_batch_category=self.payment_categories_map.get(
                        record['payment_categories_id'], None
                    ),
                    status=status,
                    description=record['description'] or '',
                    year=record['colyear'],
                    month=record['colmonth'],
                    execution_date=record['exdate'],
                    include_zero_amounts=self._web2py_bool_to_python(record['includezero']),
                    # organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE, null=True)
                    note=record['note'] or '',
                )
                finance_payment_batch.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = finance_payment_batch

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance payment batch: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import payment batches: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_payment_batches_exports(self):
        """
        Fetch records from payment batches exports and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM payment_batches_exports"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_payment_batch_export = m.FinancePaymentBatchExport(
                    finance_payment_batch=self.payment_batches_map.get(record['payment_batches_id'], None),
                    account=self.auth_user_map.get(record['auth_user_id'], None),
                    created_at=record['created_at']
                )
                finance_payment_batch_export.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = finance_payment_batch_export

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance payment batch export: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import payment batches exports: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_payment_batches_items(self):
        """
        Fetch records from payment batches items and import it in Costasiella.
        :return: None
        """
        query = """SELECT * FROM payment_batches_items"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                finance_payment_batch_item = m.FinancePaymentBatchItem(
                    finance_payment_batch=self.payment_batches_map.get(record['payment_batches_id'], None),
                    account=self.auth_user_map.get(record['auth_customer_id'], None),
                    finance_invoice=self.invoices_map.get(record['invoices_id'], None),
                    account_holder=record['accountholder'] or '',
                    account_number=record['accountnumber'] or '',
                    account_bic=record['bic'] or '',
                    mandate_signature_date=record['mandatesignaturedate'],
                    mandate_reference=record['mandatereference'] or '',
                    amount=record['amount'] or 0,
                    currency=record['currency'],
                    description=record['description'] or ''
                )
                finance_payment_batch_item.save()
                # Increase counter
                records_imported += 1

                id_map[record['id']] = finance_payment_batch_item

            except django.db.utils.IntegrityError as e:
                logger.error("Import error for finance payment batch item: %s: %s" % (
                    record['id'],
                    e
                ))

        log_message = "Import payment batches items: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logger.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _update_account_classpasses_remaining(self):
        """
        Update remaining classes for all class passes, now that the attendance has been imported.
        :return:
        """
        records_updated = 0
        classpasses = m.AccountClasspass.objects.all()
        for classpass in classpasses:
            classpass.update_classes_remaining()
            records_updated += 1

        log_message = "Calculate number of classes remaining on passes: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_updated, len(classpasses)))
        logger.info(log_message + self.get_records_import_status_display(records_updated, len(classpasses), raw=True))
