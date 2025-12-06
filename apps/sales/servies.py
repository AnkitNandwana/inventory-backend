from django.db import transaction
from .models import Sale, SaleItem
from apps.inventory.services import InventoryService

class SalesService:
    @staticmethod
    @transaction.atomic
    def create_sale(customer_name: str, items: list):
        """
        items = [{ product_id:, qty:, selling_price: }]
        """
        sale = Sale.objects.create(customer_name=customer_name)

        total = 0
        for item in items:
            InventoryService.decrease_stock(item["product_id"], item["qty"])

            total += item["qty"] * item["selling_price"]
            SaleItem.objects.create(
                sale=sale,
                product_id=item["product_id"],
                qty=item["qty"],
                selling_price=item["selling_price"]
            )

        sale.total_amount = total
        sale.save()
        return sale
