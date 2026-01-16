#here i build that logic for backend
import json
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
data_file = BASE_DIR / "data" / "products.json"

def load_products() -> List[Dict]:
    if not data_file.exists():
        return []

    try:
        with data_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def get_all_products() -> List[Dict]:
    return load_products()


#-------------this is for the create data-and insert into dummy.json---------
def save_products(products:List[dict])-> None:
    with data_file.open("w",encoding="utf-8") as f:
        json.dump(products,f,indent=2,ensure_ascii=False)

def add_product(product:Dict)->None:
    products=get_all_products()
    if any(p["sku"]==product["sku"] for p in products):
        raise ValueError ("SKU alredy exist")
    products.append(product)
    save_products(products)
    return product


#---------for delete from post data-----------------

def remove_product(id:str) ->None:
    products=get_all_products()

    for idx, p in enumerate(products):
        if p["id"] == str(id):
            deleted=products.pop(idx)
            save_products(products)
            return {'massage':"product deleted sucessfully","data":remove_product   }

#---------------UPDATE_PRODUCT-------------------------

def change_product(product_id:str,update_data:dict):
    products = get_all_products()

    for index,product in enumerate(products):
        if product["id"] == str(product_id):

            for key,value in update_data.items():
                if value is None:
                    continue


                if isinstance(value,dict) and isinstance(product.get(key),dict):
                    product[key].update(value)
                else:
                    product[key]=value

            products[index]=product
            save_products(products)
            return product

    raise ValueError("product not found")