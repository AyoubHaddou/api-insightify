from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv
load_dotenv()

# DATABASE_USER = os.getenv('DATABASE_USER')
# DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
# DATABASE_HOST = os.getenv('DATABASE_HOST')
# DATABASE_PORT = os.getenv('DATABASE_PORT')
# DATABASE_NAME = os.getenv('DATABASE_NAME')

DATABASE_USER="leavit_2"
DATABASE_PASSWORD="leavit_2"
DATABASE_HOST="0.0.0.0"
DATABASE_PORT=5432
DATABASE_NAME="leavit_2"

SQLALCHEMY_DATABASE_URL = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
if os.getenv("TESTING"):
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_TEST")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_connection():
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    return session

db = get_connection()
