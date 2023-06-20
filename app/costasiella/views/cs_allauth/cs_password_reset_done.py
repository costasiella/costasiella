from allauth.account.views import PasswordResetDoneView

from ...models import Organization


class CSPasswordResetDoneView(PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        organization = Organization.objects.all().first()

        context = super(PasswordResetDoneView, self).get_context_data(**kwargs)
        context["organization"] = organization

        return context
