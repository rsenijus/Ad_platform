from sqlalchemy import Column, Integer, String
from .db import Base


class Login(Base):

    __tablename__ = 'login'

    id = Column(Integer, primary_key=True, index=True,  unique=True)
    login = Column(String)
    password = Column(String)
    coins = Column(Integer)

class Publicity(Base):

    __tablename__ = 'publicity'

    id = Column(Integer, primary_key=True, index=True,  unique=True)
    name = Column(String)
    description = Column(String)
    author = Column(String)
    videotype = Column(String)
    imagetype = Column(String)
    moderated = Column(Integer)
    users = Column(Integer)

class Proofs(Base):
    
    __tablename__ = 'proofs'
    
    id = Column(Integer, primary_key=True, index=True,  unique=True)
    pub_id = Column(Integer)
    proof = Column(String)
    author = Column(String)
    moderated = Column(Integer)
    