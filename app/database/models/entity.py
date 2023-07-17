from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connexion import Base 

class Entity(Base):
    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'))
    name = Column(String)
    address = Column(String)
    place_id = Column(String)

    tenant = relationship("Tenant", backref="entities")