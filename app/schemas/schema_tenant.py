from pydantic import BaseModel

class Tenant(BaseModel):
    name: str 
    type: str
    website: str
    user_id : int 
    strapiTenantId : int 