import strawberry
from strawberry import auto
from typing import List, Optional
from decimal import Decimal
from .models import Purchase, PurchaseItem
from apps.supplier.schema import SupplierType
from apps.product.schema import ProductType


@strawberry.django.type(PurchaseItem)
class PurchaseItemType:
    id: auto
    product: ProductType
    qty: auto
    unit_cost: auto
    line_total: auto


@strawberry.django.type(Purchase)
class PurchaseType:
    id: auto
    supplier: SupplierType
    invoice_no: Optional[str]
    total_amount: auto
    status: auto
    created_at: auto
    items: List[PurchaseItemType]


@strawberry.input
class PurchaseItemInput:
    product_id: int
    qty: int
    unit_cost: Decimal


@strawberry.input
class PurchaseInput:
    supplier_id: int
    invoice_no: Optional[str] = None
    items: List[PurchaseItemInput]


@strawberry.input
class PurchaseUpdateInput:
    invoice_no: Optional[str] = None
    status: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    def purchases(self) -> List[PurchaseType]:
        return Purchase.objects.select_related('supplier').prefetch_related('items__product').all()
    
    @strawberry.field
    def purchase(self, id: int) -> Optional[PurchaseType]:
        try:
            return Purchase.objects.select_related('supplier').prefetch_related('items__product').get(id=id)
        except Purchase.DoesNotExist:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_purchase(self, input: PurchaseInput) -> PurchaseType:
        purchase = Purchase.objects.create(
            supplier_id=input.supplier_id,
            invoice_no=input.invoice_no
        )
        
        total_amount = Decimal("0.00")
        for item_input in input.items:
            line_total = item_input.unit_cost * item_input.qty
            PurchaseItem.objects.create(
                purchase=purchase,
                product_id=item_input.product_id,
                qty=item_input.qty,
                unit_cost=item_input.unit_cost,
                line_total=line_total
            )
            total_amount += line_total
        
        purchase.total_amount = total_amount
        purchase.save()
        return purchase
    
    @strawberry.mutation
    def update_purchase(self, id: int, input: PurchaseUpdateInput) -> Optional[PurchaseType]:
        try:
            purchase = Purchase.objects.get(id=id)
            
            if input.invoice_no is not None:
                purchase.invoice_no = input.invoice_no
            if input.status is not None:
                purchase.status = input.status
            
            purchase.save()
            return purchase
        except Purchase.DoesNotExist:
            return None
    
    @strawberry.mutation
    def delete_purchase(self, id: int) -> bool:
        try:
            purchase = Purchase.objects.get(id=id)
            purchase.delete()
            return True
        except Purchase.DoesNotExist:
            return False


schema = strawberry.Schema(query=Query, mutation=Mutation)