import pandas as pd  
from app.database.connexion import db
from app.database.models.tenant import Tenant 
from app.database.models.translation import Translation
from app.database.models.review import Review

table_columns = ['review_id','tenant_id','entity_id','text_en','rating','date','source']

def get_all_reviews_en():
    return db.query(Translation).all()

def get_reviews_en_by_tenant_id(tenant_id):
    return db.query(Review).filter_by(tenant_id=tenant_id).join(Translation).all()

def get_df_translation():
    query = (db
             .query(Review, Translation)
             .join(Translation)
             .filter_by(review_id=Review.id))
    return pd.read_sql(query.statement, query.session.bind)[table_columns]

def get_df_translation_from_tenant_id(tenant_id):
    query = (db
             .query(Review, Translation)
             .join(Translation)
             .filter_by(review_id=Review.id)
             .filter(Review.tenant_id == tenant_id))
    return pd.read_sql(query.statement, query.session.bind)[table_columns]

def get_df_translation_from_tenant_id_by_month(tenant_id, month):
    table_columns = ['review_id','tenant_id','entity_id','text_en','rating','date','source']
    query = (db
             .query(Review, Translation)
             .join(Translation)
             .filter_by(review_id=Review.id)
             .filter(Review.tenant_id == tenant_id))
    df = pd.read_sql(query.statement, query.session.bind)[table_columns]
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    year, month = map(int, month.split('-'))
    mask = (df['date'].dt.year == year) & (df['date'].dt.month == month)
    return df[mask]    