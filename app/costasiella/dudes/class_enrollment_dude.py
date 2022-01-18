from django.utils.translation import gettext as _


class ClassEnrollmentDude:
    def on_enrollment_end(self, schedule_item_enrollment):
        """
        Function to call when ending an enrollment
        - Cancel all classes after end date
        :return:
        """
        pass
