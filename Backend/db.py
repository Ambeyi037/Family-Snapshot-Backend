from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings as st

SQLALCHEMY_DATABASE_URL=f'mysql+mysqlconnector://{st.DB_USERNAME}:{st.DB_PASSWORD}@{st.DB_HOSTNAME}:{st.DB_PORT}/{st.DB_NAME}'
engine=create_engine(SQLALCHEMY_DATABASE_URL)

sessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)

