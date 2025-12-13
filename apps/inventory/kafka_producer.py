import json
import logging
from kafka import KafkaProducer
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class StockAlertProducer:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                acks='all',
                retries=3
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
    
    def send_stock_alert(self, product_data):
        """Send low stock alert to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not available")
            return False
        
        try:
            alert_message = {
                'type': 'LOW_STOCK_ALERT',
                'product_id': product_data['id'],
                'product_name': product_data['name'],
                'sku': product_data['sku'],
                'current_stock': product_data['current_stock'],
                'threshold': product_data['low_stock_threshold'],
                'timestamp': datetime.now().isoformat(),
                'severity': self._get_severity(product_data['current_stock'], product_data['low_stock_threshold'])
            }
            
            # Send to Kafka topic
            future = self.producer.send(
                'stock-alerts',
                key=product_data['id'],
                value=alert_message
            )
            
            # Wait for message to be sent
            self.producer.flush()
            logger.info(f"Stock alert sent for product {product_data['sku']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send stock alert: {e}")
            return False
    
    def _get_severity(self, current_stock, threshold):
        """Determine alert severity based on stock levels"""
        if current_stock == 0:
            return 'CRITICAL'
        elif current_stock <= threshold * 0.5:
            return 'HIGH'
        else:
            return 'MEDIUM'
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()