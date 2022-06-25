from allauth.account.views import EmailVerificationSentView

from ...models import Organization


class CSEmailVerificationSentView(EmailVerificationSentView):
    def get_context_data(self, **kwargs):
        organization = Organization.objects.all().first()

        context = super(EmailVerificationSentView, self).get_context_data(**kwargs)
        context["organization"] = organization

        return context
