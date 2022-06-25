from allauth.account.views import PasswordResetView

from ...models import Organization


class CSPasswordResetView(PasswordResetView):
    def get_context_data(self, **kwargs):
        organization = Organization.objects.all().first()

        context = super(PasswordResetView, self).get_context_data(**kwargs)
        context["organization"] = organization

        return context