import strawberry
from strawberry import auto
from typing import List, Optional
from .models import Supplier


@strawberry.django.type(Supplier)
class SupplierType:
    id: auto
    name: auto
    code: auto
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    is_active: auto
    created_at: auto


@strawberry.input
class SupplierInput:
    name: str
    code: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


@strawberry.input
class SupplierUpdateInput:
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.type
class Query:
    @strawberry.field
    def suppliers(self) -> List[SupplierType]:
        return Supplier.objects.all()
    
    @strawberry.field
    def supplier(self, id: int) -> Optional[SupplierType]:
        try:
            return Supplier.objects.get(id=id)
        except Supplier.DoesNotExist:
            return None
    
    @strawberry.field
    def supplier_by_code(self, code: str) -> Optional[SupplierType]:
        try:
            return Supplier.objects.get(code=code)
        except Supplier.DoesNotExist:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_supplier(self, input: SupplierInput) -> SupplierType:
        supplier = Supplier.objects.create(
            name=input.name,
            code=input.code,
            contact_person=input.contact_person,
            phone=input.phone,
            email=input.email,
            address=input.address,
            is_active=input.is_active
        )
        return supplier
    
    @strawberry.mutation
    def update_supplier(self, id: int, input: SupplierUpdateInput) -> Optional[SupplierType]:
        try:
            supplier = Supplier.objects.get(id=id)
            
            if input.name is not None:
                supplier.name = input.name
            if input.contact_person is not None:
                supplier.contact_person = input.contact_person
            if input.phone is not None:
                supplier.phone = input.phone
            if input.email is not None:
                supplier.email = input.email
            if input.address is not None:
                supplier.address = input.address
            if input.is_active is not None:
                supplier.is_active = input.is_active
            
            supplier.save()
            return supplier
        except Supplier.DoesNotExist:
            return None
    
    @strawberry.mutation
    def delete_supplier(self, id: int) -> bool:
        try:
            supplier = Supplier.objects.get(id=id)
            supplier.delete()
            return True
        except Supplier.DoesNotExist:
            return False


schema = strawberry.Schema(query=Query, mutation=Mutation)