from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean

Base = declarative_base()

class Secrets(Base):
    
    __tablename__ = 'secrets'

    id = Column(String(36), primary_key=True)
    env = Column(String(10))
    secret_name = Column(String(255))
    secret_value = Column(Text)
    secret_version = Column(Numeric(10,8), default=1.0)
    is_current = Column(Boolean, default=True)
