from django.apps import AppConfig


class CostasiellaConfig(AppConfig):
    # Refer to django 3.2 release notes for BigAutoField reference
    # https://docs.djangoproject.com/en/3.2/releases/3.2/
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'costasiella'

    def ready(self):
        import costasiella.signals
