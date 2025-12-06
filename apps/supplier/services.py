from .models import Supplier
from django.db import transaction

class SupplierService:
    @staticmethod
    @transaction.atomic
    def create_supplier(name: str, email: str, phone: str, address: str):
        if Supplier.objects.filter(email=email).exists():
            raise Exception("Supplier email must be unique")

        return Supplier.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
        )

    @staticmethod
    def list_suppliers():
        return Supplier.objects.order_by("name")
