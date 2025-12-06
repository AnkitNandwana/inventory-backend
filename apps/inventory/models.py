from django.db import models
from decimal import Decimal
from apps.product.models import Product
# from core.enums import TxnType

class InventoryTransaction(models.Model):
    TxnType = [
        ("IN","IN"),
        ("OUT","OUT"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transactions")
    qty = models.IntegerField()
    type = models.CharField(max_length=3, choices=TxnType)
    reference_type = models.CharField(max_length=64, null=True, blank=True)  # e.g., 'Purchase' or 'Sale'
    reference_id = models.UUIDField(null=True, blank=True)   # if using UUIDs for references
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "inventory_transactions  "
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["type"]),
        ]


class StockLot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="lots")
    qty = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    remaining_qty = models.IntegerField()
    reference = models.CharField(max_length=64, null=True, blank=True)  # e.g., PurchaseItem id
    # Index to optimize consuming lots
    class Meta:
        db_table = "stock_lots"
        indexes = [models.Index(fields=["product", "created_at"])]