import pandas as pd 
import datetime
import pytest

from app.utils.google_func import generate_entreprises_by_name, generate_reviews

def test_generate_entreprises_by_name():
    search_coord = "48.117761, -1.685869"
    search_name = "norauto"
    search_type = "car_repair"

    result = generate_entreprises_by_name(search_coord, search_name, search_type)
    
    print('result of geenrate_entreprise', result)
    print(result.columns)
    
    assert 'Norauto' in result['name'].values
    assert len(result['name'].values) > 0
    

def test_generate_reviews():
    place_id = "ChIJVWGpsYPswkcR1PXqoduJyzs"
    entity_id = 4

    result = generate_reviews(place_id, entity_id)
    
    print('result', result)
    print('type', type(result))
    assert result.shape[0] > 0
    assert result[0] == entity_id
    assert isinstance(result[1][0], int)
    assert isinstance(result[2][0], str)
    assert isinstance(result[3][0], datetime.datetime)