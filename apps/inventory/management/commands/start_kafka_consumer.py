from django.core.management.base import BaseCommand
from apps.inventory.kafka_consumer import StockAlertConsumer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start Kafka consumer for stock alerts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Kafka consumer for stock alerts...'))
        
        consumer = StockAlertConsumer()
        
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping Kafka consumer...'))
            consumer.stop_consuming()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in Kafka consumer: {e}'))
            logger.error(f'Kafka consumer error: {e}')
        finally:
            self.stdout.write(self.style.SUCCESS('Kafka consumer stopped'))