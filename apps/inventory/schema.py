import strawberry
from strawberry import auto
from typing import List, Optional
from decimal import Decimal
from .models import InventoryTransaction, StockLot
from apps.product.schema import ProductType


@strawberry.django.type(InventoryTransaction)
class InventoryTransactionType:
    id: auto
    product: ProductType
    qty: auto
    type: auto
    reference_type: Optional[str]
    unit_cost: Optional[Decimal]
    created_at: auto
    note: Optional[str]


@strawberry.django.type(StockLot)
class StockLotType:
    id: auto
    product: ProductType
    qty: auto
    unit_cost: auto
    created_at: auto
    remaining_qty: auto
    reference: Optional[str]


@strawberry.input
class InventoryTransactionInput:
    product_id: int
    qty: int
    type: str
    reference_type: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    note: Optional[str] = None


@strawberry.input
class StockLotInput:
    product_id: int
    qty: int
    unit_cost: Decimal
    reference: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    def inventory_transactions(self) -> List[InventoryTransactionType]:
        return InventoryTransaction.objects.select_related('product').all()
    
    @strawberry.field
    def inventory_transaction(self, id: int) -> Optional[InventoryTransactionType]:
        try:
            return InventoryTransaction.objects.select_related('product').get(id=id)
        except InventoryTransaction.DoesNotExist:
            return None
    
    @strawberry.field
    def stock_lots(self) -> List[StockLotType]:
        return StockLot.objects.select_related('product').all()
    
    @strawberry.field
    def stock_lot(self, id: int) -> Optional[StockLotType]:
        try:
            return StockLot.objects.select_related('product').get(id=id)
        except StockLot.DoesNotExist:
            return None
    
    @strawberry.field
    def product_stock_lots(self, product_id: int) -> List[StockLotType]:
        return StockLot.objects.filter(product_id=product_id).select_related('product')


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_inventory_transaction(self, input: InventoryTransactionInput) -> InventoryTransactionType:
        transaction = InventoryTransaction.objects.create(
            product_id=input.product_id,
            qty=input.qty,
            type=input.type,
            reference_type=input.reference_type,
            unit_cost=input.unit_cost,
            note=input.note
        )
        return transaction
    
    @strawberry.mutation
    def create_stock_lot(self, input: StockLotInput) -> StockLotType:
        stock_lot = StockLot.objects.create(
            product_id=input.product_id,
            qty=input.qty,
            unit_cost=input.unit_cost,
            remaining_qty=input.qty,
            reference=input.reference
        )
        return stock_lot


schema = strawberry.Schema(query=Query, mutation=Mutation)