from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connexion import Base 
from sqlalchemy.orm import relationship

class Tenant(Base):
    __tablename__ = 'tenant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    type = Column(String)
    website = Column(String)

    reviews = relationship("Review", backref="tenant")