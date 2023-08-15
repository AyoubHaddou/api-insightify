import pandas as pd
from app.database.connexion import db
from sentry_sdk import capture_message
from app.database.models.tenant import Tenant
from app.utils.data_processing import process_monthly_tenant_reviews, process_tenant_reviews
from app.database.models.analysis import Analysis
from app.database.models.entity import Entity
from app.database.models.review import Review
from app.database.models.translation import Translation
from logging_config import logger

def get_all_tenant():
    return db.query(Tenant).all()

def get_df_tenant():
    query = db.query(Tenant)
    return pd.read_sql(query.statement, query.session.bind)

def get_tenant_by_id(tenant_id):
    return db.query(Tenant).get(tenant_id)

def get_tenant_by_name(name):
    return db.query(Tenant).filter_by(name=name).first()

def new_tenant(tenant_name, tenant_type, tenant_url_web):
    new_enreprise = Tenant(name=tenant_name, type=tenant_type, url_web=tenant_url_web)
    db.add(new_enreprise)
    db.commit()
    capture_message('NEW TENANT')
    logger.info('New tenant add to database')
    
def get_all_tenants_id():
    return [tenant.id for tenant in db.query(Tenant).all()]

def post_tenant(tenant_name, tenant_type, tenant_url_web, user_id):
    """
    Args:
        name (str): The name of the tenant
        type (str): the type of tenant (Should match with google type. Store - restaurant - supermarket - cafe - hotel - bakery - car_repair - hair_care)
        url_web (str): Should be like www.domain.com 
    """

    # Check if Tenant is already in the database
    check_name = db.query(Tenant).filter_by(name=tenant_name).first()
    if check_name:
        raise ("Tenant already exists")

    # Create and get new tenant
    new_tenant(tenant_name, tenant_type, tenant_url_web)
    
    tenant = get_tenant_by_name(tenant_name)
    
    if tenant is None:
        raise ValueError("Tenant object is None")
    
    process_tenant_reviews(tenant, user_id)


def upadate_monthly_by_tenant(tenant_id, month, user_id):
    
    tenant = get_tenant_by_id(tenant_id)
    
    if tenant is None:
        raise ValueError("Tenant is None")
    logger.info('starting monthly process')

    return process_monthly_tenant_reviews(tenant, month, user_id)


def delete_tenant_and_all_reviews(tenant_id):

    # Obtenez le tenant par son tenant_id
    tenant = db.query(Tenant).get(tenant_id)

    if tenant is None:
        logger.info(f"Le tenant {tenant_id} n'existe pas.")
        return {'Error': "Tenant not found"}

    # Supprimer toutes les analyses liées aux commentaires du tenant en utilisant une liste en compréhension
    [delete(analysis) for analysis in db.query(Analysis).join(Review).filter(Review.tenant_id == tenant_id).all()]
    logger.info('Analysis deleted')
    
    # Supprimer toutes les traductions liées aux commentaires du tenant en utilisant une liste en compréhension
    [delete(translation) for translation in db.query(Translation).join(Review).filter(Review.tenant_id == tenant_id).all()]
    logger.info('Translation deleted')

    # Supprimer tous les commentaires liés au tenant en utilisant une liste en compréhension
    [delete(review) for review in db.query(
        Review).filter_by(tenant_id=tenant_id).all()]
    logger.info('Review deleted')

    # Supprimer toutes les entités liées au tenant en utilisant une liste en compréhension
    [delete(entity) for entity in db.query(
        Entity).filter_by(tenant_id=tenant_id).all()]
    logger.info('Entity deleted')

    # Supprimer le tenant lui-même
    delete(tenant)
    logger.info('Success : Tenant and all references deleted')
    return {'Success': "Tenant and all references deleted"}
    
def delete(row):
    if row != None:
        db.delete(row)
        db.commit()