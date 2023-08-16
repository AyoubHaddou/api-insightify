from app.database.connexion import engine, db
from sentry_sdk import capture_message
from app.collection.google_api.scripts_google import run_google_reviews_api
from app.database.crud.crud_reviews import get_df_reviews_from_name, get_df_reviews_from_name_by_month
from app.database.crud.crud_translation import get_df_translation_from_tenant_id, get_df_translation_from_tenant_id_by_month
from app.utils.database_queries import get_all_review_data_by_tenant_id
from app.utils.pnn_func import run_prediction_pnn
from app.utils.scraping_func import run_scrapping_trustpilot
from app.utils.strapi_func import send_all_analysis, send_notification_to_strapi
from app.utils.translation_func import translate_fr_to_en
from app.utils.advanced_analyse_func import run_prediction_nested_1, run_prediction_nested_2
from logging_config import logger

def insert_data_to_db(df, table_name, engine, message='200'):
    """
    Inserts data from DataFrame into a specified table in the database.
    Args:
        df (DataFrame): DataFrame containing data to insert.
        table_name (str): Name of the table in the database.
        engine: Database engine for inserting data.
        message (str): Message for logging and printing.
    """
    df.to_sql(table_name, engine, index=False, if_exists='append')
    capture_message(f"REQUESTS POSTGRES DONE - {message}")
    logger.info(f"BDD: Table {table_name} mis à jour avec succès - {message}")
      
def process_tenant_reviews(tenant, user_id=1):
    
    send_notification_to_strapi(
        notification_type = "Ajout d'une entreprise",
        notification_description = f'{tenant.name} en cours de préparation...',
        user_id = user_id, 
    )
    
    # Scrapping of Trustpilot and insert into database
    run_scrapping_trustpilot(tenant.id, tenant.website)
    
    # RUN google api function and insert into database
    run_google_reviews_api(tenant.type, tenant.name, tenant.id)
    
    # Get df with trustpilot and google reviews
    df_reviews = get_df_reviews_from_name(tenant.name)
    
    # Translate reviews in English for the model
    df_reviews = translate_fr_to_en(df_reviews)
    
    # Insert translation into database
    insert_data_to_db(df_reviews[['review_id', 'text_en', 'source_translation']], 'translation', engine)
    
    df_reviews = get_df_translation_from_tenant_id(tenant.id)
    
    categories = ['PNN', 'nested_1', 'nested_2']
    for category in categories:
        suffixe = categories.index(category) + 1
        df_reviews = run_prediction(df_reviews, category)  # Replace 'run_prediction' with the actual prediction function
        insert_data_to_db(df_reviews[['review_id', f'type_{suffixe}', f'prediction_{suffixe}', f'score_{suffixe}']]
                          .rename(columns={f'type_{suffixe}': 'type', f'prediction_{suffixe}': 'prediction', f'score_{suffixe}': 'score'}),
                          table_name='analysis', engine=engine, message=f'Analysis {category} for {tenant.name}')
        
    # get reviews from tenant_id 
    df_reviews = get_all_review_data_by_tenant_id(tenant.id)
    
    logger.info('starting STEP : SENDING TO STRAPI')

    # # Send all analyses to Strapi BDD
    send_all_analysis(df_reviews)
    
    send_notification_to_strapi(
        notification_type = "Ajout d'une entreprise",
        notification_description = f'{tenant.name} : Les analyses sont disponible',
        user_id = user_id, 
    )
    
def process_monthly_tenant_reviews(tenant, month, user_id=None):
            
    try:
        test_year, _ = map(int, month.split('-'))
        assert len(str(test_year)) == 4 
    except Exception :
        raise('Error processing. Route monthly-process need month value in format year-month. Example: 2022-02')
    
    send_notification_to_strapi(
        notification_type = "Ajout d'une entreprise",
        notification_description = f'{tenant.name} en cours de préparation...',
        user_id = user_id, 
    )
    
    
    # Faire scraping trustpilot avec argument month  
    run_scrapping_trustpilot(tenant.id, tenant.website, month=month)
    
    # Run google api 
    run_google_reviews_api(tenant.type, tenant.name, tenant.id, month=month)
    
    # Get new df with trustpilot and google reviews by month
    df_reviews = get_df_reviews_from_name_by_month(tenant.name, month=month)
    
    if df_reviews.shape[0] == 0:
        logger.info(f'No records for this date : {month}')
        return {'failed': f'No records for this date : {month}'} 
    
    # Translate reviews in English for the model
    df_reviews = translate_fr_to_en(df_reviews)
    
    # Insert translation into database
    insert_data_to_db(df_reviews[['review_id', 'text_en', 'source_translation']], 'translation', engine)
    
    df_reviews = get_df_translation_from_tenant_id_by_month(tenant.id, month)
    
    categories = ['PNN', 'nested_1', 'nested_2']
    for category in categories:
        suffixe = categories.index(category) + 1
        df_reviews = run_prediction(df_reviews, category)  # Replace 'run_prediction' with the actual prediction function
        insert_data_to_db(df_reviews[['review_id', f'type_{suffixe}', f'prediction_{suffixe}', f'score_{suffixe}']]
                          .rename(columns={f'type_{suffixe}': 'type', f'prediction_{suffixe}': 'prediction', f'score_{suffixe}': 'score'}),
                          table_name='analysis', engine=engine, message=f'Analysis {category} for {tenant.name}')
        
    # get reviews from tenant_id 
    df_reviews = get_all_review_data_by_tenant_id(tenant.id, month=month)
    
    logger.info('starting STEP : SENDING TO STRAPI')
    
    # Send all analyses to Strapi BDD
    send_all_analysis(df_reviews)
    
    send_notification_to_strapi(
        notification_type = "Ajout d'une entreprise",
        notification_description = f'{tenant.name} : Les analyses sont disponible',
        user_id = user_id, 
    )
    

def run_prediction(df, category):
    logger.info(f'prédiction {category} incoming...')
    if category == 'PNN':
        return run_prediction_pnn(df)
    elif category == 'nested_1':
        return run_prediction_nested_1(df)
    elif category == 'nested_2':
        return run_prediction_nested_2(df)
    else:
        raise('Unknown category: ' + category)