import datetime
from typing import List, Any

from PIL import Image, ImageDraw, ImageOps
import io

import Config
from client.ObjBase import ObjBase
from client.Rank import Rank
from webRequests.RequestsGet import RequestsGet



class Avatars(object):

    def __init__(self, accountId=None, small=None, medium=None, large=None):
        self.accountId = accountId      # type: str
        self.small = small              # type: str
        self.medium = medium            # type: str
        self.large = large              # type: str

    def downloadImage(self, size: str) -> io.BytesIO:
        """
        Downloads the profile picture and and returns a BytesIO buffer containing the file
        """

        if size.lower() == 'small':
            url = self.small
        elif size.lower() == 'medium':
            url = self.medium
        elif size.lower() == 'large':
            url = self.large
        else:
            raise NotImplementedError('Size identifier {} unknown.'.format(size))

        if Config.USE_NGINX:
            url = 'http://localhost:3215' + url[31:]

        resp = RequestsGet.get(url)
        img = Image.open(io.BytesIO(resp.content))

        # Create a round mask
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)

        # Apply the mask to the image
        img_round = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        img_round.putalpha(mask)

        buffer = io.BytesIO()
        img_round.save(buffer, 'PNG')

        return buffer


    def __str__(self) -> str:
        return 'Avatars<>'


class Player(ObjBase):

    def __init__(self, accountId):
        self.accountId = accountId

        self.exists = None          # type: bool
        self.username = None        # type: str
        self.rank = Rank(None)      # type: Rank
        self.dotaPlus = None        # type: bool
        self.steamId = None         # type: int
        self.avatars = Avatars()    # type: Avatars
        self.profileUrl = None      # type: str
        self.countryCode = None     # type: str
        self.wins = None            # type: int
        self.loses = None           # type: int

        self.timestamp = None       # type: datetime.datetime

    def load(self):
        """
        Loads the object from the api
        """

        # Set the timestamp
        self.timestamp = datetime.datetime.now()

        # Player infos
        data = self._loadData('players/{}'.format(self.accountId))
        if 'profile' not in data:
            self.exists = False
            return
        self.exists = True

        print('Loaded {}.'.format(data['profile']['personaname']))
        self.username = data['profile']['personaname']
        if 'rank_tier' in data:
            self.rank = Rank(data['rank_tier'])
        else:
            self.rank = Rank(None)
        self.dotaPlus = data['profile']['plus']
        self.dotaPlus = self.dotaPlus if self.dotaPlus else False
        self.steamId = data['profile']['steamid']
        self.avatars = Avatars(accountId=self.accountId,
                               small=data['profile']['avatar'],
                               medium=data['profile']['avatarmedium'],
                               large=data['profile']['avatarfull'])
        self.profileUrl = data['profile']['profileurl']
        self.countryCode = data['profile']['loccountrycode']
        self.countryCode = self.countryCode if self.countryCode else ''

        # Download the profile picture
        self.avatars.downloadImage('medium')

        # Win-lose infos
        data = self._loadData('players/{}/wl'.format(self.accountId))
        self.wins = data['win']
        self.loses = data['lose']

    @property
    def games(self):
        return self.wins + self.loses

    @property
    def winrate(self):
        return round(100 / (self.wins + self.loses) * self.wins, 2)

    def __repr__(self) -> str:
        return f'Player<id={self.accountId}, username={self.username}>'


class PlayerPeers(ObjBase):

    def __init__(self, accountId):
        self.accountId = accountId  # type: int
        self.peers = list()  # type: List[Peer]


    def load(self):
        # Peers
        data = self._loadData('players/{}/peers'.format(self.accountId))
        relevant = [p for p in data if p['with_games'] >= Config.GAMES_PLAYED_MIN]

        for p in relevant:
            peer = Peer(self.accountId, p['account_id'])
            peer.games = p['with_games']
            peer.wins = p['with_win']
            peer.timestamp = datetime.datetime.now()
            self.peers.append(peer)

    def __repr__(self) -> str:
        return f'PlayerPeers<{len(self.peers)}>'


class Peer(object):

    def __init__(self, accountId1=None, accountId2=None):
        self.accountId1 = accountId1    # type: int
        self.accountId2 = accountId2    # type: int

        self.games = None   # type: int
        self.wins = None    # type: int

        self.timestamp = None   # type: datetime.datetime

    @property
    def loses(self):
        return self.games - self.wins

    @property
    def winrate(self):
        return round(100 / self.games * self.wins, 2)

    def __repr__(self) -> str:
        return f'Peer<{self.accountId1} -> {self.accountId2} ({self.games})>'


if __name__ == '__main__':
    p = Player(123)
    p.load()


    print("")
