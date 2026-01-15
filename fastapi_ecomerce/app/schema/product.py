#---------ye post ke liye hia yani data user se lene ke liye pydantic -------------

from pydantic import (BaseModel, Field, AnyUrl,StrictFloat,EmailStr,
field_validator,# ye sirf ek hi field pe kaaam karta ahi 
model_validator ,computed_field) #if you want to give multiple field do use model_validator
from typing import Optional, List
from typing_extensions import Literal,Annotated
from uuid import UUID
from datetime import datetime

#--------------for dimention_cm dict--------------------
class DimensionCm(BaseModel):
    length:Annotated[StrictFloat,
     Field(gt=0, 
     le=50, 
     description="length of a product")]

    width: Annotated[StrictFloat, 
    Field(gt=0, 
    le=50, 
    description="widht of a product")] 

    height:Annotated[StrictFloat,
    Field(gt=0,
    le=10, 
    description="height of a product")] 

    
#-------------------------for seller dict ----------------------------------
class Seller(BaseModel):
    id: UUID
    name: Annotated[str,
        Field( min_length=6,
        max_length= 80 ,
        title="seller Name",
        description="Name of a seller (6-80) char ",
        examples=["mi store", "Realme store"])]

    email:EmailStr

    website: AnyUrl

    @field_validator("email",mode="after")
    @classmethod
    def validate_seller_email_format(cls,value=EmailStr):
        allowed_domain=[ "lenovostore.in","samsungindia.in","mistore.in","asusexclusive.in", "hpworld.in","oneplusstore.in"]
        domain=str(value).split("@")[-1].lower()

        if domain not in allowed_domain :
            raise ValueError (f"seller email domain not allowed :{domain}")
        return value

#-----------------actual main Basemodel---------------------
class Product(BaseModel):
    id: UUID
    sku: Annotated[str, Field(
        min_length=6,
        max_length=36,
        title="SKU",
        examples=["REAL-135GB-001"])]

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

    discount_percent : Annotated [int ,Field(
        ge=0,
        le=90,
        description= "Descount in percentage(0-90)")]
    
    stock: Annotated[int,Field
        (ge=0,
        title="how many items are left")]


    is_active:Annotated[bool,Field (
        description ="is porduct active ?")]

    rating:Annotated[StrictFloat , Field(
        ge= 0 , 
        le=5,
        strict=True,
        description=" Product Rating out of 5 ")]

    tags: Annotated [Optional [List[str]], Field (
        default= None, 
        max_items= 10,
        description = "up to 10 tags"
    )
    ]
    image_urls : Annotated [List[AnyUrl], Field ( description="img url's ") ]
    
    dimensions_cm :DimensionCm

    seller:Seller
    

    created_at: datetime

#this field validetor must in class not out of class 
    @field_validator("sku",mode="after")
    @classmethod
    def validate_sku_format(cls,value=str):
        if "-" not in value:
            raise ValueError("sku must have '-'")

        last=value.split("-") [-1]
        if not (len(last) ==3 and last.isdigit()):
            raise ValueError("sku must end with a 3-digit like -234")

        return value
    
    @model_validator(mode="after")
    @classmethod
    def validate_business_rule(cls, model:"product"):
        if model.stock == 0 and model.is_active == True : 
            raise ValueError ("if stock is 0 ,is_active must be false")
        

        if model.discount_percentage > 0 and model.rating == 0 : 
            raise ValueError ("discounted Price must have the rating(rating !=0)")

        return model

    @computed_field 
    @property
    def final_price(self) -> float:
        return round(self.price*(1-self.discount_percentage/100),2)    

    @computed_field
    @property
    def Volume_cm3(self) -> float:
        d=self.dimensions_cm
        return round(d.length * d.width * d.height,2)


#--------------------------UPDATE-----------------------------------------------------------------------

class DimensionCmUpdate(BaseModel):
    length:Optional[StrictFloat]=Field(gt=0)
    width:Optional[StrictFloat]=Field(gt=0)
    height:Optional[StrictFloat]=Field(gt=0)

class sellerUpadate(BaseModel):
    name:Optional[str]=Field( min_length=6,max_length= 80 )
    email:Optional[EmailStr]
    website:Optional[AnyUrl]

    @field_validator("email",mode="after")
    @classmethod
    def validate_seller_email_format(cls,value=EmailStr):
        allowed_domain=[ "lenovostore.in","samsungindia.in","mistore.in","asusexclusive.in", "hpworld.in","oneplusstore.in"]
        domain=str(value).split("@")[-1].lower()

        if domain not in allowed_domain :
            raise ValueError (f"seller email domain not allowed :{domain}")
        return value


class productUpdate(BaseModel):
    #sku: Optional[str]= Field(min_length=6,max_length=36,title="SKU",)
    name:Optional[str]=Field( min_length=6,max_length= 80 )
    description:Optional[str]=Field(max_length=200)
    category:Optional[str]
    brand:Optional[str]

    price:Optional[StrictFloat]=Field(gt=0)
    currency:Optional[Literal["INR"]] 
    
    discount_percent:Optional[int]=Field(ge=0,le=90)
    stock:Optional[int]=Field(ge=0)

    is_active:Optional[bool]

    rating:Optional[StrictFloat]=Field(ge=0,le=5)

    tags:Optional[List[str]]=Field(max_length=10)
    image_urls:Optional[List[AnyUrl]]

    dimensions_cm:Optional[DimensionCmUpdate]
    seller: Optional[sellerUpadate]
    


    '''@field_validator("sku",mode="after")
    @classmethod
    def validate_sku_format(cls,value=str):
        if "-" not in value:
            raise ValueError("sku must have '-'")

        last=value.split("-") [-1]
        if not (len(last) ==3 and last.isdigit()):
            raise ValueError("sku must end with a 3-digit like -234")

        return value'''
    
    @model_validator(mode="after")
    @classmethod
    def validate_business_rule(cls, model:"product"):
        if model.stock == 0 and model.is_active == True : 
            raise ValueError ("if stock is 0 ,is_active must be false")
        

        if model.discount_percent > 0 and model.rating == 0 : 
            raise ValueError ("discounted Price must have the rating(rating !=0)")

        return model

    @computed_field 
    @property
    def final_price(self) -> float:
        return round(self.price*(1-self.discount_percent/100),2)    

    @computed_field
    @property
    def Volume_cm3(self) -> float:
        d=self.dimensions_cm
        return round(d.length * d.width * d.height,2)





    
