from allauth.account.views import SignupView

from ...models import Organization


class CSSignUpView(SignupView):
    def get_context_data(self, **kwargs):
        organization = Organization.objects.all().first()

        context = super(SignupView, self).get_context_data(**kwargs)
        context["organization"] = organization

        return context