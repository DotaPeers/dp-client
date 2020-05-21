from webObjects.PlayerRaw import PlayerRaw
from webObjects.PlayerWL import PlayerWL
from webObjects.PlayerPeers import PlayerPeers
from webObjects.Player import Player

PLAYER_ID = 154605920

if __name__ == '__main__':
    # peers = PlayerPeers(PLAYER_ID)
    player = Player(PLAYER_ID)
    # player.recursive_load()
    pass