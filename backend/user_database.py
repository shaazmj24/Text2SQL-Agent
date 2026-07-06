import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

data_base_api = os.getenv("database_url")

engine = create_engine(data_base_api)         #connect to postgrel database

SessionLocal = sessionmaker(                  #sessionmaker (factory) creates workspaces (sessions) . session: an object backend uses to execute database operations during request
    autocommit=False,                         #prevent auto commit . only u can control
    autoflush=False,
    bind=engine                                #tellin which database to connect . it connects to engine (engine --> this posgtrel database)
)

Base = declarative_base()

def get_db():
    db = SessionLocal()                           #creates new session (instance)
    try:
        yield db                                  #yield is like return but instead of ending the function , it pauses the function . when the db session is handed to API endpoint , function resumes
    finally:
        db.close()                                 #after endpoint done using session , it closes session (user leaves table) for new user/request
                                                   #returns session to sqlalch connection pool where it can be reused by new request 
              
            