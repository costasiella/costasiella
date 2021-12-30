from django.apps import AppConfig


class CostasiellaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'costasiella'

    def ready(self):
        import costasiella.signals
