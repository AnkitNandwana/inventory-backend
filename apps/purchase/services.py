from django.db import transaction
from .models import Purchase, PurchaseItem
from apps.inventory.services import InventoryService

class PurchaseService:
    @staticmethod
    @transaction.atomic
    def create_purchase(supplier_id: int, items: list):
        """
        items = [{ product_id:, qty:, cost_price: }]
        """
        purchase = Purchase.objects.create(supplier_id=supplier_id)

        total = 0
        for item in items:
            total += item["qty"] * item["cost_price"]
            PurchaseItem.objects.create(
                purchase=purchase,
                product_id=item["product_id"],
                qty=item["qty"],
                cost_price=item["cost_price"]
            )
            InventoryService.increase_stock(item["product_id"], item["qty"])

        purchase.total_amount = total
        purchase.save()
        return purchase
