from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de producto
class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str

# Almacenamiento en memoria
products = []
next_id = 1

@app.post("/products/", response_model=Product)
def create_product(product: Product):
    """Crea un nuevo producto."""
    global next_id
    product.id = next_id
    products.append(product)
    next_id += 1
    return product

@app.get("/products/", response_model=List[Product])
def list_products():
    """Lista todos los productos."""
    return products

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Obtiene un producto por su ID."""
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product):
    """Actualiza un producto existente."""
    for index, product in enumerate(products):
        if product.id == product_id:
            products[index] = updated_product
            updated_product.id = product_id
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    """Elimina un producto por su ID."""
    for index, product in enumerate(products):
        if product.id == product_id:
            del products[index]
            return {"detail": "Product deleted"}
    raise HTTPException(status_code=404, detail="Product not found")

# Para ejecutar: uvicorn main:app --reload