import json
import logging
import pdb

from kafka import KafkaConsumer
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading

logger = logging.getLogger(__name__)

class StockAlertConsumer:
    def __init__(self):
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_STOCK_ALERTS_TOPIC,
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
                
                # Generate purchase order suggestion
                self._generate_purchase_suggestion(alert_data)
                
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
    
    def _generate_purchase_suggestion(self, alert_data):
        """Generate purchase order suggestion based on stock alert"""
        try:
            from apps.purchase.services import PurchaseOrderSuggestionService
            
            product_id = alert_data.get('product_id')
            current_stock = alert_data.get('current_stock', 0)
            threshold = alert_data.get('threshold', 0)
            
            if not product_id:
                logger.warning("No product_id in alert data, skipping PO suggestion")
                return
            
            logger.info(f"🛒 Generating purchase suggestion for product {product_id}")
            
            suggestion = PurchaseOrderSuggestionService.generate_suggestion_for_product(
                product_id=product_id,
                current_stock=current_stock,
                threshold=threshold
            )
            if suggestion:
                logger.info(f"✅ Purchase suggestion created: {suggestion.suggested_qty} units from {suggestion.supplier.name}")
                
                # Send PO suggestion to WebSocket as well
                po_alert = {
                    'type': 'PURCHASE_SUGGESTION',
                    'suggestion_id': suggestion.id,
                    'product_name': suggestion.product.name,
                    'sku': suggestion.product.sku,
                    'supplier': suggestion.supplier.name,
                    'suggested_qty': suggestion.suggested_qty,
                    'total_cost': float(suggestion.total_cost),
                    'reason': suggestion.reason
                }
                
                async_to_sync(self.channel_layer.group_send)(
                    'purchase_suggestions',
                    {
                        'type': 'purchase_suggestion_message',
                        'message': po_alert
                    }
                )
                logger.info("📋 Purchase suggestion sent to WebSocket")
            else:
                logger.warning(f"Could not generate purchase suggestion for product {product_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to generate purchase suggestion: {e}")
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