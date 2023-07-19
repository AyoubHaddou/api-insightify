from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.schemas.schema_tenant import Tenant
from app.http.guards import auth as security 
from app.utils import crud_pnn 
import app.database.crud.crud_tenant as crud_tenant

router = APIRouter(
    prefix="/tenant",
    tags=["tenant"],
    responses={404: {"description": "Resource not found."}}
)

@router.get('/all', dependencies=[Depends(security.is_authenticated)])
def get_all_tenant():
    return crud_tenant.get_all_tenant()

@router.get('/tenant-by-name', dependencies=[Depends(security.is_authenticated)])
def get_tenant_by_name_adress(name):
    if name in ['', None]:
        raise HTTPException(
            status_code=400,
            detail=f'You must give a name and adress values.'
        )
    return crud_tenant.get_tenant_by_name_adress(name)

@router.post('/new', dependencies=[Depends(security.is_authenticated)])
def post_tenant_by_name_adress(tenant: Tenant):
    if tenant.name in ['', None] or tenant.url_web in ['', None]:
        raise HTTPException(
            status_code=400,
            detail=f'You must give a name and adress values.'
        )
    return crud_tenant.post_tenant(tenant.name, tenant.type, tenant.url_web)

@router.post('/delete', dependencies=[Depends(security.is_authenticated)])
def post_tenant_by_name_adress(id: int):
    if not isinstance(id, int):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid id as number.'
        )
    return crud_tenant.delete_tenant_and_all_reviews(id)