from django.db import models
from decimal import Decimal
# from core.validators import positive_value

from django.core.exceptions import ValidationError

def clean(self):
    if self.selling_price < 0 or self.cost_price < 0:
        raise ValidationError("Prices must be non-negative")
    if self.low_stock_threshold < 0:
        raise ValidationError("low_stock_threshold cannot be negative")


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True, db_index=True)   # unique SKU
    name = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    barcode = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    selling_price = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    current_stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-updated_at"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.sku} - {self.name}"
