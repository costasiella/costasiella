from django.core.management.base import BaseCommand, CommandError, no_translations
import costasiella.models as models


class Command(BaseCommand):
    help = 'Import from OpenStudio'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    @no_translations
    def handle(self, *args, **options):
        self.stdout.write("Hello world from my import command")

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
