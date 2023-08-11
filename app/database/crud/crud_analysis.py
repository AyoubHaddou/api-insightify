from pandas import read_sql 
from app.database.connexion import db 
from app.database.models.analysis import Analysis
from app.database.models.review import Review


def get_all_analysis():
    return db.query(Analysis).all()

def get_df_analysis():
    query = db.query(Analysis)
    return read_sql(query.statement, query.session.bind)

def get_analysis_by_tenant_id(tenant_id):
    return db.query(Analysis).join(Review).filter_by(tenant_id=tenant_id)

def get_df_analysis_by_tenant_id(tenant_id):
    query = get_analysis_by_tenant_id(tenant_id)
    return read_sql(query.statement, query.session.bind)