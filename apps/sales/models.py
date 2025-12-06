from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.product.models import Product

class Sale(models.Model):
    STATUS_CHOICES = [
        ("CREATED","CREATED"),
        ("COMPLETED","COMPLETED"),
        ("CANCELLED","CANCELLED"),
    ]
    customer_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sales"
        indexes = [models.Index(fields=["created_at"])]

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.IntegerField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=16, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.qty
        super().save(*args, **kwargs)

    class Meta:
        db_table = "sale_items"
        indexes = [models.Index(fields=["product"]), models.Index(fields=["sale"])]
