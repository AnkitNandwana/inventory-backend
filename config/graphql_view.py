from strawberry.django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .schema import schema


@method_decorator(csrf_exempt, name='dispatch')
class CustomGraphQLView(GraphQLView):
    def __init__(self, **kwargs):
        super().__init__(schema=schema, **kwargs)