import strawberry
from strawberry import auto
from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404

from .models import Product, Category


@strawberry.django.type(Category)
class CategoryType:
    id: auto
    name: auto
    slug: auto
    created_at: auto


@strawberry.django.type(Product)
class ProductType:
    id: auto
    sku: auto
    name: auto
    category: Optional[CategoryType]
    barcode: Optional[str]
    cost_price: auto
    selling_price: auto
    current_stock: auto
    low_stock_threshold: auto
    is_active: auto
    created_at: auto
    updated_at: auto


@strawberry.input
class CategoryInput:
    name: str
    slug: str


@strawberry.input
class ProductInput:
    sku: str
    name: str
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    cost_price: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    current_stock: int = 0
    low_stock_threshold: int = 0
    is_active: bool = True


@strawberry.input
class ProductUpdateInput:
    name: Optional[str] = None
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    current_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    is_active: Optional[bool] = None


@strawberry.type
class Query:
    @strawberry.field
    def products(self) -> List[ProductType]:
        return Product.objects.select_related('category').all()
    
    @strawberry.field
    def product(self, id: int) -> Optional[ProductType]:
        try:
            return Product.objects.select_related('category').get(id=id)
        except Product.DoesNotExist:
            return None
    
    @strawberry.field
    def product_by_sku(self, sku: str) -> Optional[ProductType]:
        try:
            return Product.objects.select_related('category').get(sku=sku)
        except Product.DoesNotExist:
            return None
    
    @strawberry.field
    def categories(self) -> List[CategoryType]:
        return Category.objects.all()
    
    @strawberry.field
    def category(self, id: int) -> Optional[CategoryType]:
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_category(self, input: CategoryInput) -> CategoryType:
        category = Category.objects.create(
            name=input.name,
            slug=input.slug
        )
        return category
    
    @strawberry.mutation
    def create_product(self, input: ProductInput) -> ProductType:
        product = Product.objects.create(
            sku=input.sku,
            name=input.name,
            category_id=input.category_id,
            barcode=input.barcode,
            cost_price=input.cost_price,
            selling_price=input.selling_price,
            current_stock=input.current_stock,
            low_stock_threshold=input.low_stock_threshold,
            is_active=input.is_active
        )
        return product
    
    @strawberry.mutation
    def update_product(self, id: int, input: ProductUpdateInput) -> Optional[ProductType]:
        try:
            product = Product.objects.get(id=id)
            
            if input.name is not None:
                product.name = input.name
            if input.category_id is not None:
                product.category_id = input.category_id
            if input.barcode is not None:
                product.barcode = input.barcode
            if input.cost_price is not None:
                product.cost_price = input.cost_price
            if input.selling_price is not None:
                product.selling_price = input.selling_price
            if input.current_stock is not None:
                product.current_stock = input.current_stock
            if input.low_stock_threshold is not None:
                product.low_stock_threshold = input.low_stock_threshold
            if input.is_active is not None:
                product.is_active = input.is_active
            
            product.save()
            return product
        except Product.DoesNotExist:
            return None
    
    @strawberry.mutation
    def delete_product(self, id: int) -> bool:
        try:
            product = Product.objects.get(id=id)
            product.delete()
            return True
        except Product.DoesNotExist:
            return False
    
    @strawberry.mutation
    def delete_category(self, id: int) -> bool:
        try:
            category = Category.objects.get(id=id)
            category.delete()
            return True
        except Category.DoesNotExist:
            return False


schema = strawberry.Schema(query=Query, mutation=Mutation)