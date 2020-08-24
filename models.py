from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint, FLOAT, BIGINT
import sqlalchemy
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.associationproxy import association_proxy
import Config

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    peers = relationship('UserPeer', back_populates='player1', foreign_keys='UserPeer.player1_id')
    _to_peers = relationship('UserPeer', back_populates='player2', foreign_keys='UserPeer.player2_id')

    def add_peer(self, target):
        up = UserPeer(player2=target)
        self.peers.append(up)

    def __repr__(self):
        return 'User<{}>'.format(self.id)


class UserPeer(Base):
    __tablename__ = 'user_peer'

    id = Column(Integer, primary_key=True)

    player1_id = Column(Integer, ForeignKey('user.id'))
    player1 = relationship('User', back_populates='peers', foreign_keys=player1_id)
    player2_id = Column(Integer, ForeignKey('user.id'))
    player2 = relationship('User', back_populates='_to_peers', foreign_keys=player2_id)

    winrate = Column(Integer, nullable=True)

    def __repr__(self):
        return 'UserPeer<{}, {}>'.format(self.player1_id, self.player2_id)




if __name__ == '__main__':
    engine = sqlalchemy.create_engine('sqlite:///{}'.format(Config.DATABASE_NAME))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    u1 = User(name='User1')
    session.add(u1)
    u2 = User(name='User2')
    session.add(u2)
    u3 = User(name='User3')
    session.add(u3)
    session.commit()

    u1.add_peer(u2)
    u1.add_peer(u3)

    session.commit()

    print('Done')
