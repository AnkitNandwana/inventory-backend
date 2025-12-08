import strawberry
from apps.product.schema import Query as ProductQuery, Mutation as ProductMutation
from apps.supplier.schema import Query as SupplierQuery, Mutation as SupplierMutation
from apps.purchase.schema import Query as PurchaseQuery, Mutation as PurchaseMutation
from apps.sales.schema import Query as SalesQuery, Mutation as SalesMutation
from apps.inventory.schema import Query as InventoryQuery, Mutation as InventoryMutation
from apps.auth_app.schema import Query as AuthQuery, Mutation as AuthMutation


@strawberry.type
class Query(ProductQuery, SupplierQuery, PurchaseQuery, SalesQuery, InventoryQuery, AuthQuery):
    pass


@strawberry.type
class Mutation(ProductMutation, SupplierMutation, PurchaseMutation, SalesMutation, InventoryMutation, AuthMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)