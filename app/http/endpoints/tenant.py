# pylint: disable=missing-function-docstring
from app.database.crud.crud_reviews import delete_reviews_by_month_and_tenant
from app.utils.data_processing import process_monthly_tenant_reviews
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
            detail='You must give a name and url_web values.'
        )
    return crud_tenant.post_tenant(tenant.name, tenant.type, tenant.url_web)

@router.post('/delete', dependencies=[Depends(security.is_authenticated)])
def delete_tenant_by_id(tenant_id: int):
    if not isinstance(id, int):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid id as number.'
        )
    return crud_tenant.delete_tenant_and_all_reviews(tenant_id)

@router.post('/delete-month', dependencies=[Depends(security.is_authenticated)])
def delete_reviews_of_tenant_by_month(tenant_id: int, month: str):
    if not isinstance(id, int):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid id as number.'
        )
    return delete_reviews_by_month_and_tenant(tenant_id, month)

@router.post('/process-monthly-by-tenant', dependencies=[Depends(security.is_authenticated)])
def run_monthly_process_by_tenant_id(tenant_id: int, month: str):
    if not isinstance(id, int) and not isinstance(month, str):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid month as string.'
        )
    
    tenant = crud_tenant.get_tenant_by_id(tenant_id)
    return process_monthly_tenant_reviews(tenant, month)

@router.post('/process-monthly-all-tenants', dependencies=[Depends(security.is_authenticated)])
def update_month_all_tenants(month: str):
    if not isinstance(month, str):
        raise HTTPException(
            status_code=400,
            detail=f'You must give a valid id as number and valid month as string.'
        )
    list_tenant_ids = crud_tenant.get_all_tenants_id()
    for tenant_id in list_tenant_ids:
        tenant = crud_tenant.get_tenant_by_id(tenant_id)
        process_monthly_tenant_reviews(tenant, month)