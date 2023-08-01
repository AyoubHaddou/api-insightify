import pandas as pd 
from app.database.connexion import engine
from app.database.crud.crud_reviews import get_df_reviews


def seed_db():    

    tenants = {
        'name' : ['Auchan', 'Decathlon', 'Leroy Merlin', 'Norauto'],
        'type' : ['store', 'store', 'store', 'car_repair'],
        'url_web' : ['www.auchan.fr', 'www.decathlon.fr', 'www.leroymerlin.fr', 'www.norauto.fr']}

    # Tenant table
    df_tenant = pd.DataFrame(tenants)
    df_tenant.to_sql('tenant', engine, index=False, if_exists='append')
    print('Tenant table updated successfully')

    # reviws table
    df_all = pd.read_csv("app/database/all_reviews_en_july_14_pnn_and_nested_2_4.csv")
    df_reviews = df_all[['tenant_id','text', 'rating', 'date', 'source']]
    df_reviews.to_sql('review', engine, index=False, if_exists='append')
    print('reviews table updated successfully')

    # analysis table
    df_reviews = get_df_reviews()
    df = df_reviews.merge(df_all.drop('id',axis=1), on=['tenant_id','text', 'rating', 'date', 'source'])
    df = df.rename({'id': 'review_id'}, axis=1)
    
    df['type'] = 'PNN'
    df[["review_id", "type", 'prediction_1', 'score_1']].rename(columns={'prediction_1': 'prediction', 'score_1': 'score'}).to_sql('analysis', engine, index=False, if_exists='append')
    df['type'] = 'NESTED_1'
    df[["review_id", "type", 'prediction_2', 'score_2']].rename(columns={'prediction_2': 'prediction', 'score_2': 'score'}).to_sql('analysis', engine, index=False, if_exists='append')
    df['type'] = 'NESTED_2'
    df[["review_id", "type", 'prediction_3', 'score_3']].rename(columns={'prediction_3': 'prediction', 'score_3': 'score'}).to_sql('analysis', engine, index=False, if_exists='append')
    print('analysis table updated successfully')