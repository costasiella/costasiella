from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from django_celery_results.models import TaskResult
from ..modules.messages import Messages

m = Messages()

class DjangoCeleryResultTaskResultNode(DjangoObjectType):
    class Meta:
        model = TaskResult
        filter_fields = ['task_name', 'status', 'date_done']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        # user = info.context.user
        # require_login(user)

        return self._meta.model.objects.get(id=id)


class DjangoCeleryResultTaskResultQuery(graphene.ObjectType):
    django_celery_result_task_results = DjangoFilterConnectionField(DjangoCeleryResultTaskResultNode)
    django_celery_result_task_result = graphene.relay.Node.Field(DjangoCeleryResultTaskResultNode)



