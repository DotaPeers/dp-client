from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as types
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from webObjects.ObjBase import ObjBase
from webObjects.Rank import Rank

Base = declarative_base()


class RankType(types.TypeDecorator):
    """
    The SQL type for the Rank class.
    """

    impl = types.String

    def process_bind_param(self, value: Rank, dialect):
        return value.convertBack()

    def process_result_value(self, value, dialect):
        return Rank(value)


class Avatars(Base):
    __tablename__ = 'avatars'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    player = relationship('Player', back_populates='avatars')
    small = Column(String, nullable=True, default=None)
    medium = Column(String, nullable=True, default=None)
    large = Column(String, nullable=True, default=None)

    def __repr__(self) -> str:
        return 'Avatars<>'


class PlayerPeers(Base):
    __tablename__ = 'player_peer'

    # player1_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    # player1 = relationship('Parent', back_populates='peers')
    # player2_id = Column(Integer, ForeignKey('peer.id'), primary_key=True)
    # child = relationship('Peer')


class Peer(Base):
    __tablename__ = 'peer'

    player1_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    player1 = relationship('Parent', back_populates='peers')
    player2_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    player2 = relationship('Parent', back_populates='peers')



class Player(Base, ObjBase):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    accountId = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    rank = Column(RankType, nullable=True)
    dotaPlus = Column(Boolean, nullable=False)
    steamId = Column(Integer, nullable=False)
    avatars = relationship('Avatars', uselist=False, back_populates='player')
    profileUrl = Column(String, nullable=False)
    countryCode = Column(String, nullable=True)
    wins = Column(Integer, nullable=False)
    loses = Column(Integer, nullable=False)
    peers = relationship('Peers', back_populates='player1')


    def load(self):
        """
        Loads the object from the api
        """

        # Player infos
        data = self._loadData('players/{}'.format(self.accountId))

        self.username = data['profile']['personaname']
        if 'rank_tier' in data:
            self.rank = Rank(data['rank_tier'])
        else:
            self.rank = Rank(None)
        self.dotaPlus = data['profile']['plus']
        self.steamId = data['profile']['steamid']
        self.avatars = Avatars(small=data['profile']['avatar'],
                               medium=data['profile']['avatarmedium'],
                               large=data['profile']['avatarfull'])
        self.profileUrl = data['profile']['profileurl']
        self.countryCode = data['profile']['loccountrycode']

        # Win-lose infos
        data = self._loadData('players/{}/wl'.format(self.accountId))
        self.wins = data['win']
        self.loses = data['lose']

        # Peers must be loaded by an external method

    @property
    def games(self):
        return self.wins + self.loses

    @property
    def winrate(self):
        return round(100 / (self.wins + self.loses) * self.wins, 2)


    def __repr__(self) -> str:
        return 'Player<id={}, username={}>'.format(self.accountId, self.username)
