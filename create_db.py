from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app.database.connexion import Base, engine
from app.database.models.analysis import Analysis 
from app.database.models.entity import Entity 
from app.database.models.review import Review
from app.database.models.translation import Translation
from app.database.models.tenant import Tenant
from app.database.seed import seed_db 
from logging_config import logger

def init_db():
    if not database_exists(engine.url):
        print(engine.url)
        create_database(engine.url)
        logger.info('BDD CREATED')
        
    # Base.metadata.drop_all(engine)
    # logger.info('ALL TABLES DELETED')
    
    if not engine.has_table(Tenant.__tablename__):
        Base.metadata.create_all(engine)
        logger.info("TABLES CREER AVEC SUCCES")
        seed_db()
        
if __name__ == "__main__":
    init_db()