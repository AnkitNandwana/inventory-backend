"""
Test GraphQL queries for Product and Category

Example queries to test in GraphQL playground:

1. Get all products:
query {
  products {
    id
    sku
    name
    category {
      id
      name
      slug
    }
    costPrice
    sellingPrice
    currentStock
    isActive
  }
}

2. Get single product by ID:
query {
  product(id: 1) {
    id
    sku
    name
    category {
      name
    }
    costPrice
    sellingPrice
  }
}

3. Get product by SKU:
query {
  productBySku(sku: "PROD001") {
    id
    name
    category {
      name
    }
  }
}

4. Get all categories:
query {
  categories {
    id
    name
    slug
    createdAt
  }
}

5. Create a category:
mutation {
  createCategory(input: {
    name: "Electronics"
    slug: "electronics"
  }) {
    id
    name
    slug
  }
}

6. Create a product:
mutation {
  createProduct(input: {
    sku: "ELEC001"
    name: "Smartphone"
    categoryId: 1
    costPrice: "200.00"
    sellingPrice: "299.99"
    currentStock: 50
    lowStockThreshold: 10
  }) {
    id
    sku
    name
    category {
      name
    }
    costPrice
    sellingPrice
  }
}

7. Update a product:
mutation {
  updateProduct(id: 1, input: {
    sellingPrice: "279.99"
    currentStock: 45
  }) {
    id
    name
    sellingPrice
    currentStock
  }
}

8. Delete a product:
mutation {
  deleteProduct(id: 1)
}
"""