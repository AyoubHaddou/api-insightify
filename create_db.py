from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app.database.connexion import Base, engine
from app.database.models.analysis import Analysis 
from app.database.models.entity import Entity 
from app.database.models.review import Review
from app.database.models.translation import Translation
from app.database.models.tenant import Tenant
from app.database.seed import seed_db 
import numpy as np 
import pandas as pd

def init_db():
    if not database_exists(engine.url):
        create_database(engine.url)
        print("BDD CREATED")
    # Base.metadata.drop_all(engine)
    # print('ALL TABLES DELETED')
    if not engine.has_table(Tenant.__tablename__):
        Base.metadata.create_all(engine)
        print("TABLES CREER AVEC SUCCES")
        seed_db()
        
if __name__ == "__main__":
    init_db()