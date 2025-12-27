import strawberry
from strawberry import auto
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from .models import Purchase, PurchaseItem, PurchaseOrderSuggestion, ProductSupplier
from .services import PurchaseOrderSuggestionService
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


@strawberry.django.type(ProductSupplier)
class ProductSupplierType:
    id: auto
    product: ProductType
    supplier: SupplierType
    unit_cost: auto
    minimum_order_qty: auto
    lead_time_days: auto
    is_preferred: auto
    created_at: auto


@strawberry.django.type(PurchaseOrderSuggestion)
class PurchaseOrderSuggestionType:
    id: auto
    product: ProductType
    supplier: SupplierType
    suggested_qty: auto
    unit_cost: auto
    total_cost: auto
    reason: auto
    status: auto
    created_at: auto
    reviewed_at: Optional[datetime]


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


@strawberry.input
class ProductSupplierInput:
    product_id: int
    supplier_id: int
    unit_cost: Decimal
    minimum_order_qty: int = 1
    lead_time_days: int = 7
    is_preferred: bool = False


@strawberry.type
class PurchaseSuggestionsResponse:
    suggestions: List[PurchaseOrderSuggestionType]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool

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
    
    @strawberry.field
    def purchase_suggestions(
        self, 
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 5,
        product_id: Optional[int] = None,
        supplier_id: Optional[int] = None
    ) -> PurchaseSuggestionsResponse:
        queryset = PurchaseOrderSuggestion.objects.select_related('product', 'supplier').all()
        
        # Apply filters
        if status:
            queryset = queryset.filter(status=status)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        suggestions = list(queryset.order_by('-created_at')[offset:offset + limit])
        
        # Calculate pagination info
        has_next = offset + limit < total_count
        has_previous = page > 1
        
        return PurchaseSuggestionsResponse(
            suggestions=suggestions,
            total_count=total_count,
            page=page,
            limit=limit,
            has_next=has_next,
            has_previous=has_previous
        )
    
    @strawberry.field
    def purchase_suggestion(self, id: int) -> Optional[PurchaseOrderSuggestionType]:
        try:
            return PurchaseOrderSuggestion.objects.select_related('product', 'supplier').get(id=id)
        except PurchaseOrderSuggestion.DoesNotExist:
            return None
    
    @strawberry.field
    def product_suppliers(self, product_id: Optional[int] = None) -> List[ProductSupplierType]:
        queryset = ProductSupplier.objects.select_related('product', 'supplier').all()
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


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
    
    @strawberry.mutation
    def create_product_supplier(self, input: ProductSupplierInput) -> ProductSupplierType:
        return ProductSupplier.objects.create(
            product_id=input.product_id,
            supplier_id=input.supplier_id,
            unit_cost=input.unit_cost,
            minimum_order_qty=input.minimum_order_qty,
            lead_time_days=input.lead_time_days,
            is_preferred=input.is_preferred
        )
    
    @strawberry.mutation
    def approve_purchase_suggestion(self, suggestion_id: int, user_id: Optional[int] = None) -> PurchaseType:
        purchase = PurchaseOrderSuggestionService.approve_suggestion(suggestion_id, user_id)
        return purchase
    
    @strawberry.mutation
    def reject_purchase_suggestion(self, suggestion_id: int, user_id: Optional[int] = None) -> bool:
        try:
            suggestion = PurchaseOrderSuggestion.objects.get(id=suggestion_id)
            suggestion.status = 'REJECTED'
            suggestion.reviewed_at = datetime.now()
            suggestion.reviewed_by_id = user_id
            suggestion.save()
            return True
        except PurchaseOrderSuggestion.DoesNotExist:
            return False


schema = strawberry.Schema(query=Query, mutation=Mutation)