import sys
import os
import datetime

import django.db.utils
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError, no_translations
from django.utils import timezone
from django.conf import settings
import costasiella.models as m

import MySQLdb
from MySQLdb._exceptions import OperationalError
import MySQLdb.converters

import logging

logfile = os.path.join('logs', "openstudio_import_%s.log" % timezone.now().strftime("%Y-%m-%d_%H:%M"))
logging.basicConfig(filename=logfile, level=logging.INFO)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = 'Import from OpenStudio. Provide at least --db_name, --db_user and --db_password.'
        self.cursor = None  # Set later on from handle

        self.map_validity_units_cards_and_memberships = {
            'days': 'DAYS',
            'weeks': 'WEEKS',
            'months': 'MONTHS'
        }

        self.map_validity_units_subscriptions = {
            'week': 'WEEK',
            'month': 'MONTH'
        }

        self.cs_media_root = settings.MEDIA_ROOT
        self.os_media_root = None

        # Define maps
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
        self.school_levels_map = None
        self.school_locations_map = None
        self.school_locations_rooms_map = None
        self.auth_user_map = None
        self.auth_user_business_map = None
        self.customers_classcards_map = None
        self.customers_subscriptions_map = None

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
        self.school_memberships_map = self._import_school_memberships()
        self.school_classcards_map = self._import_school_classcards()
        self.school_classcards_groups_map = self._import_school_classcards_groups()
        self.school_classcards_groups_classcards_map = self._import_school_classcards_groups_classcards()
        self.school_subscriptions_map = self._import_school_subscriptions()
        self.school_subscriptions_groups_map = self._import_school_subscriptions_groups()
        self.school_subscriptions_groups_subscriptions_map = self._import_school_subscriptions_groups_subscriptions()
        self.school_subscriptions_price_map = self._import_school_subscriptions_price()
        self.school_classtypes_map = self._import_school_classtypes()
        self.school_discovery_map = self._import_school_discovery()
        self.school_levels_map = self._import_school_levels()
        locations_import_result = self._import_school_locations()
        self.school_locations_map = locations_import_result['id_map_locations']
        self.school_locations_rooms_map = locations_import_result['id_map_rooms']
        auth_user_result = self._import_auth_user()
        self.auth_user_map = auth_user_result['id_map_auth_user']
        self.auth_user_business_map = self._import_auth_user_business()
        self.customers_classcards_map = self._import_customers_classcards()
        self.customers_subscriptions_map = self._import_customers_subscriptions()

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
            logging.info("Import default organization: OK")
        else:
            self.stdout.write("Import default organization: " + self.style.ERROR("No default organization found."))
            logging.error("Import default organization: No default organization found")

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
                trial_times=record['trialtimes'] or 0,
                name=record['name'],
                description=record['description'] or "",
                price=record['price'],
                finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id'], None),
                validity=record['validity'],
                validity_unit=self.map_validity_units_cards_and_memberships.get(record['validityunit']),
                classes=record['classes'] or 0,
                unlimited=self._web2py_bool_to_python(record['unlimited']),
                organization_membership=self.school_memberships_map.get(record['school_memberships_id'], None),
                quick_stats_amount=record['quickstatsamount'] or 0,
                finance_glaccount=self.accounting_glaccounts_map.get(record['accounting_glaccounts_id'], None),
                finance_costcenter=self.accounting_costcenters_map.get(record['accounting_costcenters_id'], None)
            )
            organization_classpass.save()
            records_imported += 1

            id_map[record['id']] = organization_classpass

        log_message = "Import organization classpasses: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
                description=record['description'],
            )
            organization_classpass_group.save()
            records_imported += 1

            id_map[record['id']] = organization_classpass_group

        log_message = "Import organization classpass groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
                organization_membership=self.school_memberships_map.get(record['school_memberships_id'], None),
                quick_stats_amount=record['quickstatsamount'] or 0,
            )
            organization_subscription.save()
            records_imported += 1

            id_map[record['id']] = organization_subscription

        log_message = "Import organization subscriptions: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
                description=record['description'],
            )
            organization_subscription_group.save()
            records_imported += 1

            id_map[record['id']] = organization_subscription_group

        log_message = "Import organization subscription groups: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
                logging.error("Could not find classtype image: %s" % os_file)
            except TypeError:
                pass

            organization_classtype.save()

            records_imported += 1

            id_map[record['id']] = organization_classtype

        log_message = "Import organization classtypes: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
            id_map_rooms[record['id']] = organization_location_room

            records_imported += 1

        log_message = "Import organization locations: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        query = "SELECT * FROM auth_user WHERE id > 1"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        id_map_auth_user = {}
        id_map_auth_user_teacher_profile = {}
        records_imported = 0
        for record in records:
            record = {k.lower(): v for k, v in record.items()}

            try:
                account = m.Account(
                    is_active=not self._web2py_bool_to_python(record['trashed']), # We need to invert this
                    customer=self._web2py_bool_to_python(record['customer']),
                    teacher=self._web2py_bool_to_python(record['teacher']),
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
                    emergency=record['emergency'] or ""
                )
                account.save()
                # Create allauth email
                account.create_allauth_email()

                # Create teacher profile
                self._import_auth_user_create_teacher_profile(account, record)

                # Create account bank account record
                account.create_bank_account()

                id_map_auth_user[record['id']] = account

                records_imported += 1
            except django.db.utils.IntegrityError as e:
                logging.error("Import auth_user error for user id: %s %s : %s" % (
                    record['id'],
                    record['email'],
                    e
                ))

        log_message = "Import auth_user: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _import_auth_user_create_teacher_profile(self, account, record):
        # Create teacher profile for account
        account_teacher_profile = account.create_teacher_profile()

        # Fill fields
        account_teacher_profile.classes = self._web2py_bool_to_python(record['teaches_classes'])
        account_teacher_profile.appointments = False
        account_teacher_profile.events = self._web2py_bool_to_python(record['teaches_workshops'])
        account_teacher_profile.role = record['teacher_role'] or ""
        account_teacher_profile.education = record['education'] or ""
        account_teacher_profile.bio = record['teacher_bio'] or ""
        account_teacher_profile.url_bio = record['teacher_bio_link'] or ""
        account_teacher_profile.url_website = record['teacher_website'] or ""

        account_teacher_profile.save()

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

        log_message = "Import customer class cards: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

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

            print(record)

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
                logging.error("Import customer subscription error for user id: %s subscription id: %s : %s" % (
                    record['auth_customer_id'],
                    record['id'],
                    e
                ))

        log_message = "Import customer subscriptions: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

        return id_map

    def _update_account_classpasses_remaining(self):
        """
        Update remaining classes for all class passes, now that the attendance has been imported.
        :return:
        """
        #TODO: Write function


    def _import_os_auth_user(self):
        """
        Fetch OpenStudio users
        :param cursor: MySQL db cursor
        :return:
        """
        query = "SELECT * from auth_user"
        self.cursor.execute(query)
        print(self.cursor.fetchone())
        # print(self.cursor.fetchall())