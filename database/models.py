import os
from PIL import Image, ImageDraw, ImageOps
import io

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as types
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from webRequests.RequestsGet import RequestsGet

from webObjects.ObjBase import ObjBase
from webObjects.Rank import Rank

import Config

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
    player_id = Column(Integer, ForeignKey('player.accountId'))
    player = relationship('Player', back_populates='avatars')
    small = Column(String, nullable=True, default=None)
    medium = Column(String, nullable=True, default=None)
    large = Column(String, nullable=True, default=None)

    def downloadImage(self, size: str):
        """
        Downloads the profile picture and saves it to the profile pictures folder
        """

        if size.lower() == 'small':
            url = self.small
        elif size.lower() == 'medium':
            url = self.medium
        elif size.lower() == 'large':
            url = self.large
        else:
            raise NotImplementedError('Size identifier {} unknown.'.format(size))


        resp = RequestsGet.get(url)
        img = Image.open(io.BytesIO(resp.content))

        # Create a round mask
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)

        # Apply the mask to the image
        img_round = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        img_round.putalpha(mask)

        img_round.save('{}/{}.png'.format(Config.PROFILE_PICTURES_FOLDER, self.player.accountId))

        return True


    def __repr__(self) -> str:
        return 'Avatars<>'


class Player(Base, ObjBase):
    __tablename__ = 'player'

    accountId = Column(Integer, nullable=False, primary_key=True)
    username = Column(String, nullable=False)
    rank = Column(RankType, nullable=True)
    dotaPlus = Column(Boolean, nullable=True)
    steamId = Column(Integer, nullable=False)
    avatars = relationship('Avatars', uselist=False, back_populates='player')
    profileUrl = Column(String, nullable=False)
    countryCode = Column(String, nullable=True)
    wins = Column(Integer, nullable=False)
    loses = Column(Integer, nullable=False)

    _from_peers = relationship('Peer', back_populates='player1', foreign_keys='Peer.player1_id', lazy=True)
    _to_peers = relationship('Peer', back_populates='player2', foreign_keys='Peer.player2_id', lazy=True)

    def load(self):
        """
        Loads the object from the api
        """

        # Player infos
        data = self._loadData('players/{}'.format(self.accountId))
        print('Loaded {}.'.format(data['profile']['personaname']))

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

        # Download the profile picture
        self.avatars.downloadImage('medium')

        # Win-lose infos
        data = self._loadData('players/{}/wl'.format(self.accountId))
        self.wins = data['win']
        self.loses = data['lose']

        # Peers must be loaded by an external method

    @property
    def peers(self):
        return self._from_peers + self._to_peers

    @property
    def games(self):
        return self.wins + self.loses

    @property
    def winrate(self):
        return round(100 / (self.wins + self.loses) * self.wins, 2)

    def __repr__(self) -> str:
        return 'Player<id={}, username={}>'.format(self.accountId, self.username)


class Peer(Base):
    __tablename__ = 'peers'

    id = Column(Integer, primary_key=True)

    player1_id = Column(Integer, ForeignKey('player.accountId'))
    player1 = relationship('Player', back_populates='_from_peers', foreign_keys=player1_id)
    player2_id = Column(Integer, ForeignKey('player.accountId'))
    player2 = relationship('Player', back_populates='_to_peers', foreign_keys=player2_id)

    games = Column(Integer)
    wins = Column(Integer)

    @property
    def loses(self):
        return self.games - self.wins

    @property
    def winrate(self):
        return round(100 / self.games * self.wins, 2)

    def otherPlayer(self, yourPlayer: Player) -> Player:
        if yourPlayer != self.player1 and yourPlayer != self.player2:
            raise RuntimeError('Wrong player {} passed to peer {}.'.format(yourPlayer, self))

        if yourPlayer == self.player1:
            return self.player2

        elif yourPlayer == self.player2:
            return self.player1


    def __repr__(self):
        try:
            p1 = self.player1.username if self.player1 else None
            p2 = self.player2.username if self.player2 else None
            return 'Peer<{} <-> {}>'.format(p1, p2)
        except Exception as e:
            return str(e)
