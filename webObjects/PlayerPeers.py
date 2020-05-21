from webObjects.ObjBase import ObjBase
import Config


class PlayerPeers(ObjBase):
    """
    Represents the Peers for a player.
    Peers: Win / lose statistics with friends
    """

    def __init__(self, playerId):
        super().__init__()
        self._playerId = playerId
        self._peerList = None

        self._load()

        # Iterator variables
        self.__max = 0
        self.__current = -1     # -1 because the first row increases this number before using it

    @property
    def peers(self):
        if not self._peerList:
            self._gen_peers_list()

        return self._peerList

    def _gen_peers_list(self):
        """
        Fills self._peerList with entries, that have played more then GAMES_PLAYED_MIN together.
        """

        peerList = list()

        for p in self._data:
            peerList.append(Peer(p))

        self._peerList = list(filter(lambda x: x.games >= Config.GAMES_PLAYED_MIN, peerList))


    def __iter__(self):
        self.__max = len(self.peers)
        self.__current = -1
        return self

    def __next__(self):
        self.__current += 1
        if self.__current < self.__max:
            return self.peers[self.__current]
        raise StopIteration

    def __repr__(self) -> str:
        return 'PlayerPeers<id={}, peerCount={}>'.format(self._playerId, len(self.peers))

    def _getUrl(self):
        return 'players/{}/peers'.format(self._playerId)

# Import must be here because Pythons import System is trash
from webObjects.Player import Player


class Peer:
    """
    Represents one entry in the list of Peers
    """

    def __init__(self, data: dict):
        self._data = data

        self._playerObj = None

    def load(self):
        """
        Load the Player object for the player mentioned in this peer. This will fetch all account data for this user.
        """

        if not self._playerObj:
            self._playerObj = Player(self.accountId)

    @property
    def isLoaded(self):
        """
        Checks if the playerObj is loaded
        """

        return self.playerObj != None

    @property
    def playerObj(self) -> Player:
        """
        Returns None without calling load before.
        """

        return self._playerObj

    @property
    def accountId(self):
        return self._data.get('account_id')

    @property
    def username(self):
        return self._data.get('personaname')

    @property
    def games(self):
        return self._data.get('games')

    @property
    def wins(self):
        return self._data.get('win')

    @property
    def loses(self):
        return self.games - self.wins


    def __repr__(self):
        return 'Peer<id={}, username={}, loaded={}>'.format(self.accountId, self.username, self.isLoaded)
