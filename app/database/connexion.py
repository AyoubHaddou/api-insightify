from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv
load_dotenv()

# PGUSER = os.getenv('PGUSER')
# PGPASSWORD = os.getenv('PGPASSWORD')
# PGHOST = os.getenv('PGHOST')
# PGPORT = os.getenv('PGPORT')
# PGDATABASE = os.getenv('PGDATABASE')

PGUSER="leavit_2"
PGPASSWORD="leavit_2"
PGHOST="0.0.0.0"
PGPORT=5432
PGDATABASE="leavit_2"

SQLALCHEMY_DATABASE_URL = f'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'
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
