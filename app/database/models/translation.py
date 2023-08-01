from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.connexion import Base


class Translation(Base):

    __tablename__ = 'translation'

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('review.id'))
    text_en = Column(String)
    source_translation = Column(String)