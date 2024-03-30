from datetime import datetime,timedelta
from jose import jwt,JWTError
from . import schemas,utils,models 
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY=settings.SECRET_KEY
ALGORITHM=settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data : dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

# Email corrections
def verify_access_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,ALGORITHM)
        email : str = payload.get('person_email') # type: ignore
        print(f"Access token verified:{id}")
        if email is None:
            raise credentials_exception
        token_data = schemas.token_data(email=email)
    except JWTError:
        raise credentials_exception 
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme),db: Session=Depends(utils.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail='Could not validate the credentials',
                                         headers={"WWW-Authenticate":"Bearer"}) 
    token=verify_access_token(token,credentials_exception)
    print("Get current user executed")
    # Some changes
    user=db.query(models.Person).filter(models.Person.email==token.email).first()
    return user      