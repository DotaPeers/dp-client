from webObjects.ObjBase import ObjBase


class PlayerWL(ObjBase):
    """
    Represents the wins / loses of a player
    """

    def __init__(self, playerId):
        super().__init__()
        self._playerId = playerId

        self._load()

    @property
    def accountId(self):
        return self._playerId

    @property
    def wins(self):
        return self._data['win']

    @property
    def loses(self):
        return self._data['lose']

    @property
    def winrate(self):
        return round(100 / (self.wins + self.loses) * self.wins, 2)


    def __repr__(self) -> str:
        return 'PlayerWL<id={}>'.format(self._playerId)

    def _getUrl(self):
        return 'players/{}/wl'.format(self._playerId)

