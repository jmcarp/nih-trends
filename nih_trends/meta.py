from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from nih_trends import config

engine = create_engine(config.DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
