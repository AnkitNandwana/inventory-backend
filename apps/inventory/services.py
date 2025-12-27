from django.db import transaction
from .models import InventoryTransaction
from apps.product.models import Product

class InventoryService:
    @staticmethod
    @transaction.atomic
    def increase_stock(product_id: int, qty: int):
        product = Product.objects.get(id=product_id)
        product.current_stock += qty
        product.save()
        
        # Create inventory transaction record
        InventoryTransaction.objects.create(
            product=product,
            qty=qty,
            type="IN",
            reference_type="Purchase"
        )
        return product

    @staticmethod
    @transaction.atomic
    def decrease_stock(product_id: int, qty: int):
        product = Product.objects.get(id=product_id)
        if product.current_stock < qty:
            raise Exception("Insufficient stock")
        product.current_stock -= qty
        product.save()
        
        # Create inventory transaction record
        InventoryTransaction.objects.create(
            product=product,
            qty=qty,
            type="OUT",
            reference_type="Sale"
        )
        return product

    @staticmethod
    def check_stock(product_id: int):
        try:
            product = Product.objects.get(id=product_id)
            return product.current_stock
        except Product.DoesNotExist:
            return 0
