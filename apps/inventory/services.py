from django.db import transaction
from .models import Inventory
from apps.product.models import Product

class InventoryService:
    @staticmethod
    @transaction.atomic
    def increase_stock(product_id: int, qty: float):
        inventory, _ = Inventory.objects.get_or_create(product_id=product_id)
        inventory.quantity += qty
        inventory.save()
        return inventory

    @staticmethod
    @transaction.atomic
    def decrease_stock(product_id: int, qty: float):
        inventory = Inventory.objects.get(product_id=product_id)
        if inventory.quantity < qty:
            raise Exception("Insufficient stock")
        inventory.quantity -= qty
        inventory.save()
        return inventory

    @staticmethod
    def check_stock(product_id: int):
        inventory = Inventory.objects.filter(product_id=product_id).first()
        return inventory.quantity if inventory else 0
