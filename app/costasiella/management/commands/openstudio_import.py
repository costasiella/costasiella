import sys
import os
import datetime

from django.core.management.base import BaseCommand, CommandError, no_translations
from django.utils import timezone
import costasiella.models as m

import MySQLdb
from MySQLdb._exceptions import OperationalError
import MySQLdb.converters

import logging

logfile = os.path.join('logs', "openstudio_import_%s.log" % timezone.now().strftime("%Y-%m-%d_%H:%M"))
logging.basicConfig(filename=logfile, level=logging.DEBUG)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = 'Import from OpenStudio. Provide at least --db_name, --db_user and --db_password.'
        self.cursor = None  # Set later on from handle

        # Define maps
        self.accounting_costcenters_map = None
        self.accounting_glaccounts_map = None
        self.tax_rates_map = None
        self.payment_methods_map = None
        self.school_memberships_map = None

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
            organization = m.Organization.objects.get(pk = 100)
            organization.archived = self._web2py_bool_to_python(record['Archived'])
            organization.name = record['Name'] or ""
            organization.address = record['Address'] or ""
            organization.phone = record['Phone'] or ""
            organization.email = record['Email'] or ""
            organization.registration = record['Registration'] or ""
            organization.tax_registration = record['TaxRegistration'] or ""
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
            finance_glaccount = m.FinanceGLAccount(
                archived=self._web2py_bool_to_python(record['Archived']),
                name=record['Name'],
                code=record['AccountingCode']
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
            finance_costcenter = m.FinanceCostCenter(
                archived=self._web2py_bool_to_python(record['Archived']),
                name=record['Name'],
                code=record['AccountingCode']
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
            finance_tax_rate = m.FinanceTaxRate(
                archived=self._web2py_bool_to_python(record['Archived']),
                name=record['Name'],
                percentage=record['Percentage'],
                rate_type="IN",
                code=record['VATCodeID'] or ""
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

        records_imported = 0
        for record in records:
            finance_payment_method = m.FinancePaymentMethod(
                archived=self._web2py_bool_to_python(record['Archived']),
                name=record['Name'],
                code=record['AccountingCode'] or ""
            )
            finance_payment_method.save()
            records_imported += 1

        log_message = "Import payment methods: "
        self.stdout.write(log_message + self.get_records_import_status_display(records_imported, len(records)))
        logging.info(log_message + self.get_records_import_status_display(records_imported, len(records), raw=True))

    def _import_school_memberships(self):
        """
        Fetch school memberships and import it in Costasiella.
        :param cursor: MySQL db cursor
        :return: None
        """
        query = "SELECT * from school_memberships"
        self.cursor.execute(query)
        records = self.cursor.fetchall()

        map_validity_units = {
            'days': 'DAYS',
            'weeks': 'WEEKS',
            'months': 'MONTHS'
        }

        id_map = {}
        records_imported = 0
        for record in records:
            organization_membership = m.OrganizationMembership(
                archived=self._web2py_bool_to_python(record['Archived']),
                display_public=self._web2py_bool_to_python(record['PublicMembership']),
                display_shop=self._web2py_bool_to_python(record['PublicMembership']),
                name=record['Name'],
                description=record['Description'] or "",
                price=record['Price'] or 0,
                finance_tax_rate=self.tax_rates_map.get(record['tax_rates_id'], None),
                validity=record['Validity'],
                validity_unit=map_validity_units.get(record['ValidityUnit']),
                terms_and_conditions=record['Terms'] or "",
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