import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from .models import *
import Config


def get_session() -> Session:
    engine = sqlalchemy.create_engine('sqlite:///{}'.format(Config.DATABASE_NAME))

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session()
