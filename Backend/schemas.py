from pydantic import BaseModel,EmailStr
from typing import Optional,Union
from pydantic.types import conint
from datetime import date

class insert_person(BaseModel):
    f_name:str
    surname:str
    dob: date
    home_place: str
    occupation:str
    alive: bool
    gender: str
    submitter: Optional[int]
    email:Optional[EmailStr]
    spouse_id:Optional[int]
    password:Optional[str]
    
class update_person(BaseModel):
    f_name:Optional[str]
    surname:Optional[str]
    email:Optional[str]
    password:Optional[str]
    dob: Optional[date]
    home_place: Optional[str]
    alive: Optional[bool]
    gender: Optional[str]
    spouse_id:Optional[int]  
      
class show_person(BaseModel):
    surname:str
    f_name:str
    dob: date
    gender: str
    home_place:str
    alive:bool
    email: str
    id:int 
    spouse_id: Union[int, None] = None
    password:str 
    class Config():
        orm_mode=True
        
class insert_events(BaseModel):
    f_name:str
    surname:str
    host_title:str
    event_title:str
    venue:str
    event_date:date
    event_time:str
    created_by: int
    created_at:Optional[date]
    description:str
    
class show_events(BaseModel):
    f_name:str
    surname:str
    host_title:str
    event_title:str
    venue:str
    event_date:date
    event_time:str
    created_by: int 
    created_at: Union[date,None]=None
    description:Union[str,None]=None
    class Config():
        orm_mode=True 
        
class token(BaseModel):
    access_token: str
    token_type: str 
    logged_in_user:int   
    class Config():
        orm_mode=True 
    
class token_data(BaseModel):
    email:Optional[str] =None             