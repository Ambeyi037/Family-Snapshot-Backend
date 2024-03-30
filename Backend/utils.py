
from .db import sessionLocal
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
pwd_context=CryptContext(schemes=['bcrypt'],deprecated="auto")

def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()
            
Base = declarative_base()

def hash(password: str):
    return pwd_context.hash(password)  

def verify(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)             