from fastapi import FastAPI, HTTPException, Query,Path
from .service.products import get_all_products
from typing import Optional,Literal
from .schema.product import Product



app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello world"}
#thsi for ony the get 


@app.get("/products")
def get_product(
    name: Optional[str] = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Insert product name (case-sensitive)"),
    
    category:Literal["laptops","mobiles","accessories","electronics"]= Query(
        default=None,
        description="choose your category"),
    
    price: Optional[float] = Query(gt= 0 , 
        default=None,
        description="filter out product by their price (max price)"),
    
    order: Literal["asc", "desc"] = Query(
        default="asc",
        description="sort order (asc or desc)"),
    
    limit: int = Query(
        default=10, 
        ge=1, 
        le=100,
        description="top items are here")
):
    
    
    products = get_all_products()
    
    # Filter by name
    if name:
        needle = name.strip().lower()
        items = [p for p in products if needle in p.get("name", "").lower()]
    else:
        items = products
    
        # Filter by category
    if category: 
        items = [p for p in items if category in p.get("category", "").lower()]
        
        
    # Filter by price (less than or equal to max price)
    if price is not None:
        items = [p for p in items if p.get("price", float('inf')) <= price]
    
    
    # Sort by price (asc / desc)
    items = sorted(items, key=lambda p: p.get("price", 0), reverse=(order == "desc"))
    
    if not items:
        raise HTTPException(status_code=404, detail="No products found")


    total = len(items)              # total matching items
    limited_items = items[:limit]   # items after applying limit

    return {
    "total": total,
    "count": len(limited_items),
    "items": limited_items
}
#-------------------------------------post method --------------------------------

@app.post("/products",status_code=201)
def created_product(product:Product):
    return product.model_dump(mode="json")

























    