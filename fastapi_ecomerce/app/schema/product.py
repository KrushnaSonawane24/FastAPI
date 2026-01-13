from pydantic import BaseModel, Field, AnyUrl,StrictFloat
from typing_extensions import Annotated, Literal , Optional
from uuid import UUID
from datetime import datetime

class Product(BaseModel):
    id: UUID
    sku: Annotated[str, Field(
        min_length=6,
        max_length=36,
        title="SKU",
        examples=["3745-3532-25235-23552"])]

    name: Annotated[str,
        Field( min_length=6,
        max_length= 80 ,
        title="Product Name",
        description="Readable product name (6-80) char ")]


    description: Annotated[str, 
        Field (title="product description ",
        max_length=200, 
        description="give the short product descrioption here ") ]
   
    category: Annotated[str,
        Field(min_length=5,
        max_length=36,
        description="catrgory like mobiles/laptops/acessories/electronics",
        examples=["mobiles","laptops"])]
    
    brand : Annotated[str , Field(min_length=2,examples=["xaomi,apple"])]

    price: Annotated[StrictFloat , 
        Field( ge= 0 ,
        strict = True ,
        title= "  Actual Product price",
        description="Actual product prise here in (INR)")]

    currency:Literal ["INR"]="INR"

    discount_percentage : Annotated [int ,Field(
        ge=0,
        le=90,
        description= "Descount in percentage(0-90)")]
    
    stock: Annotated[int,Field
        (ge=1,
        title="how many items are left")]


    is_active:Annotated[bool,Field (
        description ="is porduct active ?")]

    rating:Annotated[StrictFloat , Field(
        gt= 0 , 
        le=5,
        strict=True,
        description=" Product Rating out of 5 ")]

    tags: Annotated [Optional [list[str]], Field (
        default= None, 
        max_items= 10,
        description = "up to 10 tags"
    )
    ]
    image_urls : Annotated [list[AnyUrl], Field ( description="img url's ",min_items=1  ) ]

    created_at: datetime


    
    
    