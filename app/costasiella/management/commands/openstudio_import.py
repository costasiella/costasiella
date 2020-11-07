import sys

from django.core.management.base import BaseCommand, CommandError, no_translations
import costasiella.models as models



class Command(BaseCommand):
    help = 'Import from OpenStudio. Provide at least --db_name, --db_user and --db_password.'

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

    def _yes_or_no(self, question):
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            self.stdout.write("Import command stopped.")
            sys.exit(1)
        else:
            return self._yes_or_no("Uhhhh... please enter ")

    @no_translations
    def handle(self, *args, **options):
        self.stdout.write("OpenStudio DB connection info:")
        self.stdout.write("-----")
        self.stdout.write("name: %s" % options['db_name'])
        self.stdout.write("user: %s" % options['db_user'])
        self.stdout.write("password: %s" % options['db_password'])
        self.stdout.write("host: %s" % options['db_host'])
        self.stdout.write("port: %s" % options['db_port'])
        self.stdout.write("-----")
        self.stdout.write("")

        response = self._yes_or_no("Is the above information correct?")

        if response:
            print("hello world!")




        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
