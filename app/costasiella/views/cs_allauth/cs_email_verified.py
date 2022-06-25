from django.views.generic import TemplateView

from ...models import Organization


class CSEmailVerifiedView(TemplateView):
    def get_context_data(self, **kwargs):
        organization = Organization.objects.all().first()

        context = super(TemplateView, self).get_context_data(**kwargs)
        context["organization"] = organization

        return context
