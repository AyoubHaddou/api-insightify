# pylint: disable=missing-function-docstring
from app.database.crud.crud_reviews import delete_reviews_by_month_and_tenant
from app.utils.data_processing import process_monthly_tenant_reviews
from app.schemas.schema_tenant import Tenant
from app.http.guards import auth as security 
import app.database.crud.crud_tenant as crud_tenant
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    responses={404: {"description": "Resource not found."}}
)

@router.get('/all', dependencies=[Depends(security.is_authenticated)])
def get_all_reviews():
    pass 

@router.get('/reviews-by-tenant-id', dependencies=[Depends(security.is_authenticated)])
def get_review_by_review_id(tenant_id):
    if not isinstance(tenant_id, int):
        raise HTTPException(
            status_code=400,
            detail=f'tenant_id must be integer.'
        )
    pass 

@router.get('/review-by-review-id', dependencies=[Depends(security.is_authenticated)])
def get_reviews_by_tenant_id(tenant_id):
    if not isinstance(tenant_id, int):
        raise HTTPException(
            status_code=400,
            detail=f'tenant_id must be integer.'
        )
    pass 

@router.get('/reviews-by-list-review-id', dependencies=[Depends(security.is_authenticated)])
def get_review_by_list_tenant_id(list_tenant_id: list):
    if not isinstance(list_tenant_id, int):
        raise HTTPException(
            status_code=400,
            detail=f'tenant_id must be integer.'
        )
    pass 