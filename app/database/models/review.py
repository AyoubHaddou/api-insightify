from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connexion import Base 
from app.database.models.analysis import Analysis 

class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'))
    text = Column(String)
    rating = Column(Integer)
    date = Column(String)
    source = Column(String)

    analyses = relationship("Analysis", backref="review")