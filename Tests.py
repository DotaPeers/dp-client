# from webObjects.PlayerRaw import PlayerRaw
# from webObjects.PlayerWL import PlayerWL
# from webObjects.PlayerPeers import PlayerPeers
# from webObjects.Player import Player

from database.database import get_session
from database.models import *

PLAYER_ID = 154605920
ID_BASTI = 95157943

if __name__ == '__main__':
    # player = Player(PLAYER_ID)
    # player.recursive_load(None)

    session = get_session()

    player = Player(accountId=PLAYER_ID)
    player.load()

    session.add(player)

    # a = session.query(Player).filter_by(accountId=PLAYER_ID).first()
    # b = session.query(Player)[1]
    # a.peers.append(Peer())

    session.commit()

    pass
