from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from itertools import chain
from optparse import make_option
import os
import shutil
import sys


class Command(BaseCommand):
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
                self.stdout.write("Orphaned file cleanup stopped.")
                sys.exit(1)
            else:
                return False
        else:
            return self._yes_or_no("Please enter y or n")

    def handle(self, **options):
        ORPHANED_APPS_MEDIABASE_DIRS = settings.ORPHANED_APPS_MEDIABASE_DIRS

        for app in ORPHANED_APPS_MEDIABASE_DIRS.keys():
            if 'root' in ORPHANED_APPS_MEDIABASE_DIRS[app]:
                needed_files = []
                all_files = []
                possible_empty_dirs = []
                empty_dirs = []
                total_freed_bytes = 0
                total_freed = '0'
                delete_files = []
                skip = ORPHANED_APPS_MEDIABASE_DIRS[app].get('skip', ())
                exclude = ORPHANED_APPS_MEDIABASE_DIRS[app].get('exclude', ())

                for model in ContentType.objects.filter(app_label=app):
                    mc = model.model_class()
                    if mc is None:
                        continue
                    fields = []
                    for field in mc._meta.fields:
                        if field.get_internal_type() == 'FileField' or field.get_internal_type() == 'ImageField':
                            fields.append(field.name)
                    # we have found a model with FileFields
                    if len(fields) > 0:
                        files = mc.objects.all().values_list(*fields)
                        needed_files.extend(
                            [os.path.join(settings.MEDIA_ROOT, file) for file in filter(None,
                                                                                        chain.from_iterable(files))]
                        )

                # traverse root folder and store all files and empty directories
                def should_skip(dir):
                    for skip_dir in skip:
                        if dir.startswith(skip_dir):
                            return True
                    return False

                # process each root of the app
                app_roots = ORPHANED_APPS_MEDIABASE_DIRS[app]['root']
                # if isinstance(app_roots, basestring): # backwards compatibility
                app_roots = [app_roots]
                for app_root in app_roots:
                    for root, dirs, files in os.walk(app_root):
                        if should_skip(root):
                            continue
                        if len(files) > 0:
                            for basename in files:
                                if basename not in exclude:
                                    all_files.append(os.path.join(root, basename))
                        elif not os.path.samefile(root, app_root):
                            possible_empty_dirs.append(root)

                # ignore empty dirs with subdirs + files
                for ed in possible_empty_dirs:
                    dont_delete = False
                    for files in all_files:
                        try:
                            if files.index(ed) == 0:
                                dont_delete = True
                        except ValueError:
                            pass
                    for skip_dir in skip:
                        try:
                            if (skip_dir.index(ed) == 0):
                                dont_delete = True
                        except ValueError:
                            pass
                    if not dont_delete:
                        empty_dirs.append(ed)

                # select deleted files (delete_files = all_files - needed_files)
                aa = set(all_files)
                delete_files = list(aa.difference(needed_files))
                delete_files.sort()
                empty_dirs.sort()
                empty_dirs = set(empty_dirs) #remove possible duplicates

                # to be freed
                for df in delete_files:
                    total_freed_bytes += os.path.getsize(df)
                total_freed = "%0.1f MB" % (total_freed_bytes/(1024*1024.0))

                # only show
                print("\r\n=== %s ===" % app)
                if len(empty_dirs) > 0:
                    print("\r\nFollowing empty dirs will be removed:\r\n")
                    for file in empty_dirs:
                        print(" ", file)

                if len(delete_files) > 0:
                    print("\r\nFollowing files will be deleted:\r\n")
                    for file in delete_files:
                        print(" ", file)
                    print("\r\n%s Files will be deleted, and "\
                        " %s will be freed.\r\n" % (len(delete_files), total_freed))
                else:
                    print("No files to delete!")

                if len(empty_dirs) or len(delete_files):
                    delete_ok = self._yes_or_no(
                        "\r\nCan the items above be deleted?"
                    )

                    if delete_ok:
                        print("Deleting files and empty directories...")
                        # DELETE NOW!
                        for file in delete_files:
                            os.remove(file)
                        for dirs in empty_dirs:
                            shutil.rmtree(dirs, ignore_errors=True)
                        # End cleanup
                        print("Done")
