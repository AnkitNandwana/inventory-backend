from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'
    
    def ready(self):
        """Import signals when Django starts"""
        # import apps.inventory.signals  # Kafka version
        # import apps.inventory.signals_websocket  # WebSocket-only version
        # import apps.inventory.signals_hybrid  # Hybrid: WebSocket + Kafka
        import apps.inventory.signals_kafka_only  # Kafka → WebSocket (single path)
