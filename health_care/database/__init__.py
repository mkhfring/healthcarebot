from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import BotConfig

engine = create_engine(BotConfig.database_url)
BaseModle = declarative_base(bind=engine)
DBsession = sessionmaker(bind=engine)
session = DBsession()