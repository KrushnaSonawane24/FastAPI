from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Query,Path,Request,Depends
from .service.products import get_all_products,add_product ,remove_product ,change_product
from typing import Optional,Literal
from fastapi.responses import JSONResponse
from .schema.product import Product,productUpdate
from uuid import uuid4,UUID
from datetime import datetime



load_dotenv("app/.env")
app = FastAPI()

@app.middleware("http")
async def lifecycle(request:Request,call_next):
    print("before request")
    responce = await call_next(request)
    #responce["lifecycle"]="was inside"
    print("after request")
    return responce#["lifecycle"]

def common_logic():
    return "hello there "

@app.get("/",response_model=dict)
def root(dep=Depends(common_logic)):
    DB_path=os.getenv('base_url')
    #return {"message": "welcome to fastapi","dependancy":dep,"data_path":DB_path}
    return JSONResponse (status_code=202,content={"message": "welcome to fastapi","dependancy":dep,"data_path":DB_path})



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

@app.get("/products/{product_id}", response_model=dict)
def get_product_by_id(product_id:str=Path(...,min_length=36,max_length=36,description="UUID of the product")):
            products= get_all_products()

            for product in products:
                if product['id']==product_id:
                    return product
            raise HTTPException(status_code=404,detail="product no fount!")
                    
    
#-------------------------------------post method --------------------------------

@app.post("/products",status_code=201)
def created_product(product:Product):
    product_dict=product.model_dump(mode="json")
    product_dict["id"]=str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    try:
        add_product(product_dict)
    except ValueError as e :
        raise HTTPException(status_code=400,detail=str(e))

    return product.model_dump(mode="json")


#------------delete--------------

@app.delete("/products/{product_id}")
def delete_product(product_id:UUID=Path(
    ...,description="product UUID ")
    ):
    try:
        responce=remove_product(str(product_id))
          
        return responce
    except Exception as e :
        raise HTTPException(status_code=400,detail=str(e))

    
#--------------UPDATE----------------------------

@app.patch("/product/{product_id}")
def update_product(product_id:UUID=Path(...,description="product UUID "),payload:productUpdate=...,):
    
    try:
        update_product = change_product(str(product_id),payload.model_dump(mode="json",exclude_unset=True))
        return update_product

    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))
    






















    