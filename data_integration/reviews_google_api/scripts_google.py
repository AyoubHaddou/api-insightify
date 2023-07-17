import pandas as pd

from data_integration.helpers.google_func import generate_entreprises_by_name, generate_reviews, all_coord
from app.database.connexion import engine

def run_google_reviews_api(type, name, id):
    
    print('Starting to search google api reviews...')
    
    first_coord = all_coord[0]
    other_coord = all_coord[1:]
    df_all = generate_entreprises_by_name(coord=first_coord, keyword=name, type=type)
    
    for coord in other_coord:
        df_second = generate_entreprises_by_name(coord=coord, keyword=name, type=type)
        df_all = pd.concat([df_all, df_second])
    
    df_all = df_all[df_all.name.str.contains(name)]
    df_all['tenant_id'] = id
    
    df_all[['tenant_id', 'name', 'address', 'place_id']].to_sql('entity', engine, index=False, if_exists='append') 
    print('Table entity updated')

    df_all[['rating', 'text', 'date']] = df_all['place_id'].apply(generate_reviews)
    df_all = df_all.explode(['rating', 'text', 'date'])
    df_all = df_all[(df_all.text.isna() == False) & (df_all.text.values != '') & (df_all.text.str.len() < 512)]
    df_all['source'] = 'google'
    print('shape of google reviews datafram: ', df_all.shape)
    
    df_all[['tenant_id', 'text', 'rating', 'date', 'source']].to_sql('review', engine, index=False, if_exists='append') 
    df_all[['tenant_id', 'text', 'rating', 'date', 'source']].to_csv(f'review_google_{name}.csv', index=False) 
    print('Table review updated')