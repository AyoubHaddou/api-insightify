import pandas as pd 
from app.database.connexion import db 
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
