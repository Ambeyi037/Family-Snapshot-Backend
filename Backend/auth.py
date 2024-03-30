from fastapi import APIRouter, Depends,HTTPException,status
from .utils import get_db
from sqlalchemy.orm import Session
from .models import Person
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .utils import verify
from .tokgen import create_access_token
from .schemas import token

router_auth=APIRouter(tags=["Authentication"])

@router_auth.post("/login",response_model=token)
def login(login_credentials : OAuth2PasswordRequestForm = Depends(),db: Session=Depends(get_db)):
    # Email changes
    person=db.query(Person).filter(Person.email==login_credentials.username).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={"detail":"Requested person does not exist"})
    if not verify(login_credentials.password,person.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail={"detail":"Invalid username or password"})
    access_token=create_access_token(data={"person_email":person.email})
    print(person.id)
    
    return {"access_token": access_token,"token_type":"bearer","logged_in_user": person.id}
    # 7.27