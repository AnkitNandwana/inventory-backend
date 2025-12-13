import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.product.models import Product
from .kafka_producer import StockAlertProducer

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def check_stock_levels(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when Product model is saved.
    Checks if stock is below threshold and sends alert to Kafka.
    """
    # Skip if this is a new product creation
    if created:
        return
    
    # Check if current stock is at or below threshold
    if instance.current_stock <= instance.low_stock_threshold:
        logger.info(f"Low stock detected for {instance.sku}: {instance.current_stock} <= {instance.low_stock_threshold}")
        
        # Prepare product data for Kafka message
        product_data = {
            'id': instance.id,
            'name': instance.name,
            'sku': instance.sku,
            'current_stock': instance.current_stock,
            'low_stock_threshold': instance.low_stock_threshold,
            'category': instance.category.name if instance.category else None
        }
        
        # Send alert to Kafka
        producer = StockAlertProducer()
        success = producer.send_stock_alert(product_data)
        producer.close()
        
        if success:
            logger.info(f"Stock alert sent successfully for product {instance.sku}")
        else:
            logger.error(f"Failed to send stock alert for product {instance.sku}")
    else:
        logger.debug(f"Stock levels normal for {instance.sku}: {instance.current_stock} > {instance.low_stock_threshold}")