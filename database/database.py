import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session
from .models import *
import Config


def get_session(drop_all=False) -> Session:
    engine = sqlalchemy.create_engine('sqlite:///{}'.format(Config.DATABASE_NAME))
    if drop_all:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))

    return Session()
