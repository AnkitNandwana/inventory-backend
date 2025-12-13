from django.urls import path
from strawberry.django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from .schema import schema
from .test_views import simulate_stock_update, get_low_stock_products

app_name = 'inventory'

urlpatterns = [
    path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema)), name='inventory-graphql'),
    path('test/update-stock/', simulate_stock_update, name='test-stock-update'),
    path('test/low-stock/', get_low_stock_products, name='test-low-stock'),
]