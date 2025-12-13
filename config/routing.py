from django.urls import path
from apps.inventory.consumers import StockAlertWebSocketConsumer

websocket_urlpatterns = [
    path('ws/stock-alerts/', StockAlertWebSocketConsumer.as_asgi()),
]