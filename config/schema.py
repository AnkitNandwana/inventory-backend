import strawberry
from apps.product.schema import Query as ProductQuery, Mutation as ProductMutation
from apps.supplier.schema import Query as SupplierQuery, Mutation as SupplierMutation
from apps.purchase.schema import Query as PurchaseQuery, Mutation as PurchaseMutation
from apps.sales.schema import Query as SalesQuery, Mutation as SalesMutation
from apps.inventory.schema import Query as InventoryQuery, Mutation as InventoryMutation


@strawberry.type
class Query(ProductQuery, SupplierQuery, PurchaseQuery, SalesQuery, InventoryQuery):
    pass


@strawberry.type
class Mutation(ProductMutation, SupplierMutation, PurchaseMutation, SalesMutation, InventoryMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)