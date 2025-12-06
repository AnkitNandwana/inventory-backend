import strawberry
from strawberry import auto
from typing import List, Optional
from decimal import Decimal
from .models import Sale, SaleItem
from apps.product.schema import ProductType


@strawberry.django.type(SaleItem)
class SaleItemType:
    id: auto
    product: ProductType
    qty: auto
    unit_price: auto
    line_total: auto


@strawberry.django.type(Sale)
class SaleType:
    id: auto
    customer_name: auto
    total_amount: auto
    status: auto
    created_at: auto
    items: List[SaleItemType]


@strawberry.input
class SaleItemInput:
    product_id: int
    qty: int
    unit_price: Decimal


@strawberry.input
class SaleInput:
    customer_name: str
    items: List[SaleItemInput]


@strawberry.input
class SaleUpdateInput:
    customer_name: Optional[str] = None
    status: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    def sales(self) -> List[SaleType]:
        return Sale.objects.prefetch_related('items__product').all()
    
    @strawberry.field
    def sale(self, id: int) -> Optional[SaleType]:
        try:
            return Sale.objects.prefetch_related('items__product').get(id=id)
        except Sale.DoesNotExist:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_sale(self, input: SaleInput) -> SaleType:
        sale = Sale.objects.create(
            customer_name=input.customer_name
        )
        
        total_amount = Decimal("0.00")
        for item_input in input.items:
            line_total = item_input.unit_price * item_input.qty
            SaleItem.objects.create(
                sale=sale,
                product_id=item_input.product_id,
                qty=item_input.qty,
                unit_price=item_input.unit_price,
                line_total=line_total
            )
            total_amount += line_total
        
        sale.total_amount = total_amount
        sale.save()
        return sale
    
    @strawberry.mutation
    def update_sale(self, id: int, input: SaleUpdateInput) -> Optional[SaleType]:
        try:
            sale = Sale.objects.get(id=id)
            
            if input.customer_name is not None:
                sale.customer_name = input.customer_name
            if input.status is not None:
                sale.status = input.status
            
            sale.save()
            return sale
        except Sale.DoesNotExist:
            return None
    
    @strawberry.mutation
    def delete_sale(self, id: int) -> bool:
        try:
            sale = Sale.objects.get(id=id)
            sale.delete()
            return True
        except Sale.DoesNotExist:
            return False


schema = strawberry.Schema(query=Query, mutation=Mutation)