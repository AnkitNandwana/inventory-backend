from django.urls import path
from apps.inventory.consumers import StockAlertWebSocketConsumer, PurchaseSuggestionWebSocketConsumer

websocket_urlpatterns = [
    path('ws/stock-alerts/', StockAlertWebSocketConsumer.as_asgi()),
    path('ws/purchase-suggestions/', PurchaseSuggestionWebSocketConsumer.as_asgi()),
]