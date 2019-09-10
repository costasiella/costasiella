from django.apps import AppConfig


class CostasiellaConfig(AppConfig):
    name = 'costasiella'

    def ready(self):
        import costasiella.signals
