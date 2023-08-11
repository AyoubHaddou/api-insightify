import pandas as pd
from app.database.crud.crud_entity import get_df_entities_by_tenant_id

from app.utils.google_func import generate_reviews, all_coord, generate_entreprises_by_name
from app.database.connexion import engine
from sentry_sdk import capture_message


def run_google_reviews_api(tenant_type, tenant_name, tenant_id, month=None):


    if month is None :
                
        first_coord = all_coord[0]
        other_coord = all_coord[1:]
        df_all = generate_entreprises_by_name(search_coord=first_coord, search_name=tenant_name, search_type=tenant_type)
        
        for coord in other_coord:
            df_second = generate_entreprises_by_name(search_coord=coord, search_name=tenant_name, search_type=tenant_type)
            df_all = pd.concat([df_all, df_second])
        
        capture_message('COLLECT BY GOOGLE API DONE')
        df_all = df_all[df_all.name.str.contains(tenant_name)]
        df_all['tenant_id'] = tenant_id
        
        df_all[['tenant_id', 'name', 'address', 'place_id']].to_sql('entity', engine, index=False, if_exists='append') 
        print('Table entity updated')


    df_entities = get_df_entities_by_tenant_id(tenant_id).rename(columns={'id':'entity_id'})
    
    print('Starting google api reviews...')
    df_entities[['entity_id','rating', 'text', 'date']] = df_entities.apply(lambda x : generate_reviews(x['place_id'], x['entity_id'], month=month), axis=1)
    df_entities = df_entities.explode(['rating', 'text', 'date'])
    df_entities.text = df_entities.text.astype(str)
    df_entities = df_entities.dropna()
    df_entities['text'] = df_entities['text'].str.strip().str[0:511]
    print('shape of google reviews datafram before filters: ', df_entities.shape)

    df_entities = df_entities[(df_entities.text.isna() == False) & (df_entities.text.values != '') & (df_entities.text.str.len() < 512)]
    print('shape of google reviews datafram after filters: ', df_entities.shape)
    df_entities['source'] = 'google'

    df_entities[['tenant_id', 'entity_id', 'text', 'rating', 'date', 'source']].to_sql('review', engine, index=False, if_exists='append') 
    print('Table review updated')
    capture_message('REQUESTS POSTGRES DONE')