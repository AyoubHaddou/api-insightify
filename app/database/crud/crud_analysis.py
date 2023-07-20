import pandas as pd 
from app.database.connexion import db 
from app.database.models.analysis import Analysis
from app.database.models.review import Review


def get_all_analysis():
    return db.query(Analysis).all()

def get_df_analysis():
    query = db.query(Analysis)
    return pd.read_sql(query.statement, query.session.bind)

def get_df_analysis_from_tenant_id(tenant_id):
    query = db.query(Analysis).join(Review).filter_by(tenant_id=tenant_id)
    return pd.read_sql(query.statement, query.session.bind)
