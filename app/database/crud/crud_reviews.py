import pandas as pd 
from sqlalchemy import text
from app.database.connexion import db, engine 
from app.database.models.review import Review
from app.database.models.tenant import Tenant

def get_all_reviews():
    return db.query(Review).all()

def get_reviews_by_entreprise_id(id_entreprise):
    return db.query(Review).filter_by(id_entreprise=id_entreprise).all()

def get_df_reviews():
    query = db.query(Review)
    return pd.read_sql(query.statement, query.session.bind)

def get_df_reviews_from_name(name):
    query = db.query(Review).join(Tenant).filter_by(name=name)
    return pd.read_sql(query.statement, query.session.bind).rename(columns={'id': 'review_id'})

def get_df_reviews_from_name_by_month(name, month):
    df = get_df_reviews_from_name(name)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    year, month = map(int, month.split('-'))
    mask = (df['date'].dt.year == year) & (df['date'].dt.month == month)
    return df[mask]    


def delete_reviews_by_month_and_tenant(tenant_id, month):
    year, month = map(int, month.split('-'))
    
    query = text(
        "DELETE FROM translation "
        "WHERE review_id IN ("
        "    SELECT id FROM review "
        "    WHERE tenant_id = :tenant_id "
        "    AND (date LIKE :year_month || '-%' OR date LIKE :year_month || '-%')"
        "); "
        "DELETE FROM analysis "
        "WHERE review_id IN ("
        "    SELECT id FROM review "
        "    WHERE tenant_id = :tenant_id "
        "    AND (date LIKE :year_month || '-%' OR date LIKE :year_month || '-%')"
        "); "
        "DELETE FROM review "
        "WHERE tenant_id = :tenant_id "
        "AND (date LIKE :year_month || '-%' OR date LIKE :year_month || '-%');"
    )
    
    with engine.connect() as connection:
        connection.execute(query, tenant_id=tenant_id, year_month=f'{year}-{month:02}')