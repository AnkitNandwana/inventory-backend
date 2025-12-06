from django.db import transaction
from .models import Product, ProductCategory

class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(name: str, category_id: int, sku: str, unit: str, price: float):
        if Product.objects.filter(sku=sku).exists():
            raise Exception("SKU must be unique")

        return Product.objects.create(
            name=name,
            category_id=category_id,
            sku=sku,
            unit=unit,
            price=price,
        )

    @staticmethod
    @transaction.atomic
    def update_price(product_id: int, price: float):
        if price <= 0:
            raise Exception("Price must be greater than zero")
        product = Product.objects.get(id=product_id)
        product.price = price
        product.save()
        return product

    @staticmethod
    def list_products():
        return Product.objects.all().order_by("name")
