# pylint: disable=missing-function-docstring
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schema_tenant import Tenant
from app.http.guards import auth as security 
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
def get_tenant_by_name(name):
    if name in ['', None]:
        raise HTTPException(
            status_code=400,
            detail=f'You must give a name value.'
        )
    return crud_tenant.get_tenant_by_name(name)

@router.post('/new', dependencies=[Depends(security.is_authenticated)])
def post_tenant_by_name_and_url(tenant: Tenant):
    if tenant.name in ['', None] or tenant.url_web in ['', None]:
        raise HTTPException(
            status_code=400,
            detail='You must give a name and adress values.'
        )
    return crud_tenant.post_tenant(tenant.name, tenant.type, tenant.url_web)

@router.post('/delete', dependencies=[Depends(security.is_authenticated)])
def delete_tenant_by_id(id: int):
    if not isinstance(id, int):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid id as number.'
        )
    return crud_tenant.delete_tenant_and_all_reviews(id)

@router.patch('/update-tenant', dependencies=[Depends(security.is_authenticated)])
def update_month_tenant_by_id(id: int, month: str):
    if not isinstance(id, int) and not isinstance(month, str):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid month as string.'
        )
    pass 

@router.patch('/update-all-tenants', dependencies=[Depends(security.is_authenticated)])
def update_month_all_tenants(month):
    if not isinstance(month, str):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid id as number and valid month as string.'
        )
    pass 