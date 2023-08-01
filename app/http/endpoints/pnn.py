from fastapi import APIRouter, Depends, HTTPException
from app.http.guards import auth as security 
from app.utils import crud_pnn 

router = APIRouter(
    prefix="/pnn",
    tags=["positive-negative-neutral"],
    responses={404: {"description": "Resource not found."}}
)

@router.post('/single', dependencies=[Depends(security.is_authenticated)])
def prediction_single_row(text:str):
    if len(text) < 1 or len(text) > 512:
        raise HTTPException(
            status_code=400,
            detail=f'Please send a text between 1 and 512 characters'
        )
    return crud_pnn.predict_single_row(text)

@router.post('/multi', dependencies=[Depends(security.is_authenticated)])
def prediction_multi_row(texts_list: list):
    if not isinstance(texts_list, list):
        raise HTTPException(status_code=400, detail=f'Please provide a list of text')
    for text in texts_list: 
        if len(text) < 1 or len(text) > 512:
            raise HTTPException(status_code=400, detail=f'Please provides only texts between 1 and 512 characters')
    return crud_pnn.predict_multi_rows(texts_list)