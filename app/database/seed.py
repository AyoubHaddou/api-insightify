import pandas as pd 
from app.database.connexion import engine
from app.database.models.analysis import Analysis 
from app.database.models.entity import Entity 
from app.database.models.review import Review
from app.database.models.translation import Translation
from app.database.models.tenant import Tenant

def seed_db():  

    tables = [Tenant, Entity, Review, Translation, Analysis]

    for table in tables:    
        df = pd.read_csv(f'app/database/seed/seed_{table.__tablename__}.csv').drop(columns='id')
        df.to_sql(table.__tablename__, engine, index=False, if_exists='append')