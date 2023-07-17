from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.connexion import Base 


class Analysis(Base):
    __tablename__ = 'analysis'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    prediction = Column(String)
    score = Column(Float)
    review_id = Column(Integer, ForeignKey('review.id'))