from app.utils.crud_advanced_analyse import check_text, model_zero_shot
from app.utils.crud_pnn import predict_multi_rows, translator
from app.database.connexion import db, engine
from app.database.crud.crud_reviews import get_df_reviews_from_name 
from app.database.models.tenant import Tenant
import pandas as pd 
import subprocess
import os
from data_integration.helpers.strapi_func import send_all_analysis, send_json_by_type, list_label_nested
from data_integration.reviews_google_api.scripts_google import run_google_reviews_api

def get_all_tenant():
    return db.query(Tenant).all()

def get_df_tenant():
    query = db.query(Tenant)
    return pd.read_sql(query.statement, query.session.bind)

def get_tenant_by_name(name):
    return db.query(Tenant).filter_by(name = name).first()

def post_tenant(name, type, url_web):
    """
    Args:
        name (str): The name of the tenant
        type (str): the type of tenant (Should match with google type. Store - restaurant - supermarket - cafe - hotel - bakery - car_repair - hair_care)
        url_web (str): Should be like www.domain.com 
    Returns:
        tenant: dict  
    """
    
    # Check if Tenant is already in the database
    check = name in [i.name for i in db.query(Tenant).all()]
    if check:
        raise("Tenant already exists")
    
    # Create and get new tenant 
    new_enreprise = Tenant(name = name, type=type, url_web = url_web)
    db.add(new_enreprise)
    db.commit()
    tenant = get_tenant_by_name(name)
    
    # Scrapping of Trustpilot
    run_scrapping_trustpilot(tenant, url_web)
        
    # # RUN google api function 
    run_google_reviews_api(tenant.type, tenant.name, tenant.id)

    # Get df with trustpilot and google reviews  
    df_reviews = get_df_reviews_from_name(name)
   
    # Translate reviews in english for the modele 
    df_reviews = translate_fr_to_en(df_reviews)
    
    df_reviews = run_prediction_pnn(df_reviews)
    
    df_reviews[['review_id','type', 'prediction_1','score_1']].rename(columns={'prediction_1': 'prediction', 'score_1': 'score'}).to_sql('analysis', engine, index=False, if_exists='append') 
    print("BDD: Table analysis mis à jour avec succés pour l'analyse PNN")

    df_reviews = run_prediction_nested_1(df_reviews)
    
    df_reviews[['review_id','type', 'prediction_2','score_2']].rename(columns={'prediction_2': 'prediction', 'score_2': 'score'}).to_sql('analysis', engine, index=False, if_exists='append') 
    print('Table analysis mis à jour avec la prediction nested_1')
    
    df_reviews = run_prediction_nested_2(df_reviews)
    
    df_reviews[['review_id','type', 'prediction_3','score_3']].rename(columns={'prediction_3': 'prediction', 'score_3': 'score'}).to_sql('analysis', engine, index=False, if_exists='append') 
    print('Table analysis mis à jour avec la prediction nested_2')
    
    # # Send all analysis to strapi.
    send_all_analysis(df_reviews)
    
    return tenant


def run_prediction_pnn(df):
    
    print('Predictions PNN des avis en cours...')
    
    pred = predict_multi_rows(df.text.to_list())
    df[['prediction_1','score_1']] = pred 
    df['type'] = 'PNN' 
    
    return df 

def run_prediction_nested_1(df):
    
    print('Predictions nested_1 des avis en cours...')
    
    df[['prediction_2','score_2']] = df.apply(lambda x: check_text(model_zero_shot, x['text'], [i for i in list_label_nested[x['prediction_1']].keys()]), axis=1)
    df['type'] = 'nested_1'
    
    return df 

def run_prediction_nested_2(df):
    
    print('Predictions nested_2 des avis en cours...')
    
    df[['prediction_3','score_3']] = df.apply(lambda x: check_text(model_zero_shot, x['text'],  list_label_nested[x['prediction_1']][x['prediction_2']]), axis=1)
    df['type'] = 'nested_2'
    
    return df   

def translate_fr_to_en(df):
    
    print('Traduction des avis en cours...')
    
    traduction = translator(df.text.to_list())
    df['text'] = [i['translation_text'] for i in traduction]
    
    return df  
    
def run_scrapping_trustpilot(tenant, url_web):
    
    print('Starting scrapping function for trustpilot')

    os.environ['TENANT_URL'] = url_web
    os.environ['TENANT_ID'] = str(tenant.id) 
    
    # Chemin vers le répertoire racine du projet Scrapy
    project_directory = 'data_integration/scraping/trustpilot/trustpilot'

    # Obtention de l'emplacement d'origine
    original_directory = os.getcwd()

    try:
        print('Starting web scraping...')
        # Changement vers le répertoire du projet Scrapy
        os.chdir(project_directory)
        
        # Construction de la commande à exécuter
        command = 'scrapy crawl trustpilotreviews'

        # Exécution de la commande avec les variables d'environnement
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Attend la fin de l'exécution du processus
    finally:
        # Retour à l'emplacement d'origine
        os.chdir(original_directory)
        print('web scraping completed')
        
        
# # A voir : 
# def run_scrapping_trustpilot(tenant, url_web):

#     print('Starting scraping function for trustpilot')

#     # Chemin vers le répertoire racine du projet Scrapy
#     project_directory = 'data_integration/scraping/trustpilot/trustpilot'

#     # Obtention de l'emplacement d'origine
#     original_directory = os.getcwd()

#     try:
#         print('Starting web scraping...')
#         # Changement vers le répertoire du projet Scrapy
#         os.chdir(project_directory)

#         # Construction de la commande à exécuter avec les variables incorporées
#         command = (
#             f'scrapy crawl trustpilotreviews -a TENANT_URL={url_web} -a TENANT_ID={tenant.id} '
#             f'-a PGUSER={os.getenv("PGUSER")} -a PGPASSWORD={os.getenv("PGPASSWORD")} '
#             f'-a PGHOST={os.getenv("PGHOST")} -a PGPORT={os.getenv("PGPORT")} '
#             f'-a PGDATABASE={os.getenv("PGDATABASE")}'
#         )

#         # Exécution de la commande
#         process = subprocess.Popen(command, shell=True)
#         process.wait()  # Attend la fin de l'exécution du processus
#     finally:
#         # Retour à l'emplacement d'origine
#         os.chdir(original_directory)
#         print('Web scraping completed')
