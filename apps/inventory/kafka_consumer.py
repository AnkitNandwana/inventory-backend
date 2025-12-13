import json
import logging
from kafka import KafkaConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading

logger = logging.getLogger(__name__)

class StockAlertConsumer:
    def __init__(self):
        try:
            self.consumer = KafkaConsumer(
                'stock-alerts',
                bootstrap_servers=['localhost:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                group_id='stock-alert-group',
                auto_offset_reset='latest'
            )
            self.channel_layer = get_channel_layer()
            self.running = False
            logger.info("Kafka consumer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            self.consumer = None
    
    def start_consuming(self):
        """Start consuming messages from Kafka and forward to WebSocket"""
        if not self.consumer:
            logger.error("Kafka consumer not available")
            return
        
        self.running = True
        logger.info("🚀 Starting Kafka consumer for stock alerts...")
        logger.info(f"📡 Listening on topic: stock-alerts")
        logger.info(f"🔗 Bootstrap servers: {self.consumer.config.get('bootstrap_servers', 'Unknown')}")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                alert_data = message.value
                logger.info(f"📨 Kafka message received: {alert_data}")
                logger.info(f"🔄 Processing alert for product: {alert_data.get('sku', 'Unknown')}")
                
                # Forward message to WebSocket clients
                self._send_to_websocket(alert_data)
                
                logger.info(f"✅ Kafka->WebSocket flow completed for {alert_data.get('sku', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"❌ Error in Kafka consumer: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            self.consumer.close()
    
    def _send_to_websocket(self, alert_data):
        """Send alert data to WebSocket group"""
        try:
            if self.channel_layer:
                logger.info(f"📤 Sending to WebSocket group 'stock_alerts': {alert_data['sku']}")
                
                async_to_sync(self.channel_layer.group_send)(
                    'stock_alerts',
                    {
                        'type': 'stock_alert_message',
                        'message': alert_data
                    }
                )
                logger.info(f"✅ Alert forwarded to WebSocket clients for {alert_data['sku']}")
                
                # Log successful delivery
                logger.info("📊 Message sent to WebSocket group 'stock_alerts'")
            else:
                logger.error("❌ Channel layer not available")
        except Exception as e:
            logger.error(f"❌ Failed to send to WebSocket: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def stop_consuming(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        logger.info("🛑 Kafka consumer stopped")
    
    def start_in_thread(self):
        """Start consumer in a separate thread"""
        thread = threading.Thread(target=self.start_consuming, daemon=True)
        thread.start()
        return thread