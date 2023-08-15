import pandas as pd 
import datetime
import pytest

from app.utils.google_func import generate_entreprises_by_name, generate_reviews

def test_generate_entreprises_by_name():
    search_coord = "50.6292,3.0573"
    search_name = "Paul France"
    search_type = "bakery"

    result = generate_entreprises_by_name(search_coord, search_name, search_type)
    
    assert 'Paul' in result['name'].values
    assert result.shape[0] > 0
    

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