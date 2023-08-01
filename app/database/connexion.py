from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os 
from dotenv import load_dotenv
load_dotenv()

PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')
PGHOST = os.getenv('PGHOST')
PGPORT = os.getenv('PGPORT')
PGDATABASE = os.getenv('PGDATABASE')

SQLALCHEMY_DATABASE_URL = f'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = DatabaseSession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def get_connection():
    with session_scope() as session:
        return session

db = get_connection()