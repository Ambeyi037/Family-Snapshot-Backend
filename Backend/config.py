from pydantic import BaseSettings

# Checks the environment variables in the system
class Settings(BaseSettings):        
    DB_HOSTNAME:str
    DB_PORT:str
    DB_PASSWORD:str 
    DB_NAME:str
    DB_USERNAME:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    class Config:
        env_file=".env"       
 
settings=Settings()

# print(set(settings))      
        