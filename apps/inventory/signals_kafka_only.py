import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.product.models import Product
from datetime import datetime
from .kafka_producer import StockAlertProducer

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def send_kafka_stock_alert(sender, instance, created, **kwargs):
    """Send stock alert via Kafka only (Kafka consumer forwards to WebSocket)"""
    if created:
        return
    
    if instance.current_stock <= instance.low_stock_threshold:
        logger.info(f"🚨 Low stock detected for {instance.sku}: {instance.current_stock} <= {instance.low_stock_threshold}")
        
        # Send to Kafka only (Kafka consumer will forward to WebSocket)
        try:
            producer = StockAlertProducer()
            product_data = {
                'id': instance.id,
                'name': instance.name,
                'sku': instance.sku,
                'current_stock': instance.current_stock,
                'low_stock_threshold': instance.low_stock_threshold,
            }
            success = producer.send_stock_alert(product_data)
            producer.close()
            
            if success:
                logger.info(f"✅ Kafka alert sent for {instance.sku} (will be forwarded to WebSocket)")
            else:
                logger.error(f"❌ Kafka alert failed for {instance.sku}")
        except Exception as e:
            logger.error(f"❌ Kafka unavailable for {instance.sku}: {e}")
    else:
        logger.debug(f"Stock levels normal for {instance.sku}: {instance.current_stock} > {instance.low_stock_threshold}")