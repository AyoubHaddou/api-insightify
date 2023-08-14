# pylint: disable=missing-function-docstring
from app.http.guards import auth as security 
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