from pydantic import BaseModel

class Tenant(BaseModel):
    name: str 
    type: str
    url_web: str
    user_id : int 