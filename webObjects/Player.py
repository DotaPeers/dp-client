from webObjects.PlayerRaw import PlayerRaw
from webObjects.PlayerWL import PlayerWL
from webObjects.PlayerPeers import PlayerPeers
import Config


class Player:
    """
    Represents a DotA2 player with all of his data
    """

    def __init__(self, playerId):
        self._playerId = playerId
        self._playerRaw = PlayerRaw(playerId)
        self._playerWL = PlayerWL(playerId)
        self._playerPeers = PlayerPeers(playerId)
        print('Loaded {}'.format(self))


    @property
    def accountId(self):
        return self._playerId

    @property
    def player(self):
        return self._playerRaw

    @property
    def winlose(self):
        return self._playerWL

    @property
    def peers(self):
        return self._playerPeers


    def recursive_load(self, parent, depth=0):
        """
        Recursively loads the player objects for the peers as deep as MAX_RECURSION_DEPTH iterations
        :param parent: The Player that is connected to this player via a peer.
        :param depth: The current depth
        """

        if depth >= Config.MAX_RECURSION_DEPTH:
            return

        for peer in self.peers:
            """
            Only load if the peers player is unequal to the parent.
            This prevents unnecessary loops because when player A is connected to player B via a peer, player B is also
            connected to player A. Following the peer from B -> A when coming straight from A is useless, since it will
            create a loop A -> B -> A -> B ... until the recursion depth is reached.
            """
            if parent == None or parent.accountId != peer.accountId:
                peer.load()
                peer.playerObj.recursive_load(self, depth=depth + 1)
            else:
                # print('    Skipping {}'.format(peer))
                pass

    def __repr__(self):
        return 'Player<id={}, username={}>'.format(self.accountId, self.player.username)
