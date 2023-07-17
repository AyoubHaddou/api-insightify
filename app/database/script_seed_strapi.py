
import pandas as pd 
from data_integration.helpers.strapi_func import send_json_by_type


df = pd.read_csv('model/all_reviews_en_july_14_pnn_and_nested_2_4.csv').rename({'id':'review_id'}, axis=1)
types = ['PNN', 'text_negative', 'text_neutral', 'text_positive']
for id in df.tenant_id.unique():
    for type in types:
        send_json_by_type(df, id, type)