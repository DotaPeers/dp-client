from webObjects.ObjBase import ObjBase
from webObjects.Avatar import Avatar
from webObjects.Rank import Rank


class PlayerRaw(ObjBase):
    """
    Represents the general information part of a player
    """

    def __init__(self, playerId):
        super().__init__()
        self._playerId = playerId

        self._load()

    @property
    def accountId(self):
        return self._data['profile']['account_id']

    @property
    def username(self):
        return self._data['profile']['personaname']

    @property
    def rank(self):
        if 'rank_tier' in self._data:
            return Rank(self._data['rank_tier'])

        else:
            return Rank(None)

    @property
    def dotaPlus(self):
        return self._data['profile']['plus']

    @property
    def steamId(self):
        return self._data['profile']['steamid']

    @property
    def avatars(self):
        return Avatar(self._data['profile']['avatar'], self._data['profile']['avatarmedium'], self._data['profile']['avatarfull'])

    @property
    def profileUrl(self):
        return self._data['profile']['profileurl']

    @property
    def countryCode(self):
        return self._data['profile']['loccountrycode']


    def __repr__(self) -> str:
        return 'Player<id={}, username={}>'.format(self.accountId, self.username)

    def _getUrl(self):
        return 'players/{}'.format(self._playerId)
