from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.product.models import Product
from apps.supplier.models import Supplier

class Purchase(models.Model):
    STATUS_CHOICES = [
        ("CREATED","CREATED"),
        ("RECEIVED","RECEIVED"),
        ("CANCELLED","CANCELLED"),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchases")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    invoice_no = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchases"
        indexes = [models.Index(fields=["created_at"]), models.Index(fields=["invoice_no"])]

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=16, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.unit_cost * self.qty
        super().save(*args, **kwargs)

    class Meta:
        db_table = "purchase_items"
        indexes = [models.Index(fields=["product"]), models.Index(fields=["purchase"])]
