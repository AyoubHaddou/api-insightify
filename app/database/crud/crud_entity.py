from pandas import read_sql 
from app.database.connexion import db 
from app.database.models.entity import Entity
from app.database.models.review import Review
from app.database.models.tenant import Tenant

def get_all_entity():
    return db.query(Entity).all()

def get_df_entity():
    query = db.query(Entity)
    return read_sql(query.statement, query.session.bind)

def get_entity_by_review_id(review_id):
    return db.query(Entity).join(Review).filter_by(review_id=review_id)

def get_df_entity_by_review_id(review_id):
    query = get_entity_by_review_id(review_id)
    return read_sql(query.statement, query.session.bind)

def get_df_entities_by_tenant_id(tenant_id):
    query = db.query(Entity).filter_by(tenant_id=tenant_id)
    return read_sql(query.statement, query.session.bind)
    