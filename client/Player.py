import datetime
from PIL import Image, ImageDraw, ImageOps
import io

import Config
from client.ObjBase import ObjBase
from client.Rank import Rank
from webRequests.RequestsGet import RequestsGet


PEERS_GAMES_MIN = 200
PROFILE_PICTURES_PATH = 'profilePictures'


class ProfilePicture(object):

    accountId = None
    data = None

    def __init__(self, accountId=None):
        self.accountId = accountId


class Avatars(object):

    accountId = None
    small  = None
    medium = None
    large  = None
    profilePicture = None

    def __init__(self, accountId=None, small=None, medium=None, large=None):
        self.accountId = accountId
        self.small = small
        self.medium = medium
        self.large = large

    def __del__(self):
        if self.profilePicture:
            self.profilePicture.close()

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

        buffer = io.BytesIO()
        img_round.save(buffer, 'PNG')
        self.profilePicture = buffer

        return True


    def __str__(self) -> str:
        return 'Avatars<>'


class Player(ObjBase):

    def __init__(self, accountId):
        self.accountId = accountId

    accountId = None
    username = None
    rank = Rank(None)
    dotaPlus = None
    steamId = None
    avatars = Avatars()
    profileUrl = None
    countryCode = None
    wins = None
    loses = None

    peers = list()

    timestamp = None

    def load(self):
        """
        Loads the object from the api
        """

        # Set the timestamp
        self.timestamp = datetime.datetime.now()

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
        self.avatars = Avatars(accountId=self.accountId,
                               small=data['profile']['avatar'],
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

        # Peers
        data = self._loadData('players/{}/peers'.format(self.accountId))
        relevant = [p for p in data if p['with_games'] >= PEERS_GAMES_MIN]

        for p in relevant:
            peer = Peer(self.accountId, p['account_id'])
            peer.games = p['with_games']
            peer.wins = p['with_win']
            peer.timestamp = datetime.datetime.now()
            self.peers.append(peer)

    @property
    def games(self):
        return self.wins + self.loses

    @property
    def winrate(self):
        return round(100 / (self.wins + self.loses) * self.wins, 2)

    def __str__(self) -> str:
        return 'Player<id={}, username={}>'.format(self.accountId, self.username)


class Peer(object):

    def __init__(self, player1=None, player2=None):
        self.player1 = player1
        self.player2 = player2

    player1 = None
    player2 = None

    games = None
    wins = None

    timestamp = None

    @property
    def loses(self):
        return self.games - self.wins

    @property
    def winrate(self):
        return round(100 / self.games * self.wins, 2)

    def __repr__(self):
        return 'Peer<{} -> {}>'.format(self.player1, self.player2)


if __name__ == '__main__':
    p = Player(154605920)
    p.load()

    print("")
