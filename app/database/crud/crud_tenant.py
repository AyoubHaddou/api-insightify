from app.utils.crud_advanced_analyse import check_text, model_zero_shot
from app.utils.crud_pnn import predict_multi_rows, translator
from app.database.connexion import db, engine
from app.database.crud.crud_reviews import get_df_reviews_from_name
from app.database.models.tenant import Tenant
import pandas as pd
import subprocess
import os
from app.utils.strapi_func import send_all_analysis, list_label_nested
from app.collection.google_api.scripts_google import run_google_reviews_api
from app.database.models.analysis import Analysis
from app.database.models.entity import Entity
from app.database.models.review import Review


def get_all_tenant():
    return db.query(Tenant).all()


def get_df_tenant():
    query = db.query(Tenant)
    return pd.read_sql(query.statement, query.session.bind)


def get_tenant_by_name(name):
    return db.query(Tenant).filter_by(name=name).first()


def post_tenant(tenant_name, tenant_type, tenant_url_web):
    """
    Args:
        name (str): The name of the tenant
        type (str): the type of tenant (Should match with google type. Store - restaurant - supermarket - cafe - hotel - bakery - car_repair - hair_care)
        url_web (str): Should be like www.domain.com 
    Returns:
        tenant: dict  
    """

    # Check if Tenant is already in the database
    check_name = tenant_name in [i.name for i in db.query(Tenant).all()]
    if check_name:
        raise ("Tenant already exists")

    # Create and get new tenant
    new_enreprise = Tenant(name=tenant_name, type=tenant_type, url_web=tenant_url_web)
    db.add(new_enreprise)
    db.commit()
    tenant = get_tenant_by_name(tenant_name)


    # Scrapping of Trustpilot and insert into database
    run_scrapping_trustpilot(tenant.id, tenant_url_web)

    # RUN google api function and insert into database
    run_google_reviews_api(tenant.type, tenant.name, tenant.id)

    # Get df with trustpilot and google reviews
    df_reviews = get_df_reviews_from_name(tenant_name)

    # Translate reviews in english for the modele 
    df_reviews = translate_fr_to_en(df_reviews)
    
    # Insert translation into database
    (df_reviews[['review_id', 'text_en', 'source_translation']]
     .to_sql('translation', engine, index=False, if_exists='append')
    )
    
    # PNN prediction
    df_reviews = run_prediction_pnn(df_reviews)

    # Insert analysis into database
    (df_reviews[['review_id', 'type_1', 'prediction_1', 'score_1']]
     .rename(columns={'prediction_1': 'prediction', 'score_1': 'score', 'type_1': 'type'})
     .to_sql('analysis', engine, index=False, if_exists='append')
    )
    print("BDD: Table analysis mis à jour avec succés pour l'analyse PNN")

    # Nested_1 prediction
    df_reviews = run_prediction_nested_1(df_reviews)

    # Insert analysis into database
    (df_reviews[['review_id', 'type_2', 'prediction_2', 'score_2']]
     .rename(columns={'prediction_2': 'prediction', 'score_2': 'score', 'type_2': 'type'})
     .to_sql('analysis', engine, index=False, if_exists='append')
    )
    print('Table analysis mis à jour avec la prediction nested_1')

    # Nested_2 prediction
    df_reviews = run_prediction_nested_2(df_reviews)
    
    # Insert analysis into database
    (df_reviews[['review_id', 'type_3', 'prediction_3', 'score_3']]
     .rename(columns={'prediction_3': 'prediction', 'score_3': 'score', 'type_3': 'type'})
     .to_sql('analysis', engine, index=False, if_exists='append')
    )
    print('Table analysis mis à jour avec la prediction nested_2')
    
    # # # Send all analysis to strapi.
    # send_all_analysis(df_reviews)

    return tenant

def delete_tenant_and_all_reviews(tenant_id):

    # Obtenez le tenant par son tenant_id
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()

    if tenant is not None:
        # Supprimer toutes les analyses liées aux commentaires du tenant en utilisant une liste en compréhension
        [delete(analysis) for analysis in db.query(Analysis).join(Review).filter(Review.tenant_id == tenant_id).all()]
        print('Analysis deleted')

        # Supprimer tous les commentaires liés au tenant en utilisant une liste en compréhension
        [delete(review) for review in db.query(
            Review).filter_by(tenant_id=tenant_id).all()]
        print('Review deleted')

        # Supprimer toutes les entités liées au tenant en utilisant une liste en compréhension
        [delete(entity) for entity in db.query(
            Entity).filter_by(tenant_id=tenant_id).all()]
        print('Entity deleted')

        # Supprimer le tenant lui-même
        delete(tenant)
        print('Success, Tenant and all references deleted')
        return {'Success': "Tenant and all references deleted"}
    else:
        print("Le tenant avec tenant_id spécifié n'existe pas.")
        return {'Error': "Tenant not found"}

def run_prediction_pnn(df):

    print('Predictions PNN des avis en cours...')

    pred = predict_multi_rows(df.text_en.to_list())
    pred = pd.Series([v for v in pred.values()])
    df[['prediction_1', 'score_1']] = pred
    df['type_1'] = 'PNN'

    return df


def run_prediction_nested_1(df):

    print('Predictions nested_1 des avis en cours...')

    df[['prediction_2', 'score_2']] = df.apply(lambda x: check_text(model_zero_shot, x['text_en'], [
                                               i for i in list_label_nested[x['prediction_1']].keys()]), axis=1)
    
    df['type_2'] = 'nested_1'
    return df


def run_prediction_nested_2(df):

    print('Predictions nested_2 des avis en cours...')

    df[['prediction_3', 'score_3']] = df.apply(lambda x: check_text(
        model_zero_shot, x['text_en'],  list_label_nested[x['prediction_1']][x['prediction_2']]), axis=1)
    df['type_3'] = 'nested_2'

    return df


def translate_fr_to_en(df):

    print('Traduction des avis en cours...')

    traduction = translator(df.text.to_list())
    df['text_en'] = [i['translation_text'] for i in traduction]
    
    # rendre le translation name dynamique si je chhange le translator.model
     
    df['source_translation'] = 'Helsinki-NLP/opus-mt-fr-en'
    

    return df


def run_scrapping_trustpilot(tenant_id, url_web):
    
    print('Starting scrapping function for trustpilot')

    os.environ['TENANT_URL'] = url_web
    os.environ['TENANT_ID'] = str(tenant_id) 
    
    # Chemin vers le répertoire racine du projet Scrapy
    project_directory = 'app/collection/scraping/trustpilot/trustpilot'

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

def delete(row):
    if row != None:
        db.delete(row)
        db.commit()