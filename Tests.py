# from webObjects.PlayerRaw import PlayerRaw
# from webObjects.PlayerWL import PlayerWL
# from webObjects.PlayerPeers import PlayerPeers
# from webObjects.Player import Player

from database.database import get_session
from database.models import *
from webObjects.ObjBase import ObjBase
import Config

PLAYER_ID = 154605920
ID_BASTI = 95157943


class PeerLoader(ObjBase):

    def __init__(self, player, session):
        self.player = player
        self.session = session

    def load(self):
        return self._load(self.player)

    def _load(self, player, updatePeers=False, recursionDepth=0):
        if recursionDepth > Config.MAX_RECURSION_DEPTH:
            return

        existingPeers = player._from_peers

        if not existingPeers or updatePeers:
            data = self._loadData('players/{}/peers'.format(player.accountId))
            relevant = [p for p in data if p['with_games'] >= Config.GAMES_PLAYED_MIN]

            for p in relevant:
                target = self._get_player(p['account_id'])
                peers1 = self.session.query(Peer).filter_by(player1=target, player2=player).all()
                peers2 = self.session.query(Peer).filter_by(player1=player, player2=target).all()
                if not peers1 and not peers2:
                    self._add_peer(player, target, p['with_games'], p['with_win'])

                self.session.commit()
                self._load(target, updatePeers=updatePeers, recursionDepth=recursionDepth + 1)


    def _add_peer(self, player, target, games, wins):
        """
        Adds a peer from player to target
        """

        peer = Peer(player2=target, games=games, wins=wins)
        player._from_peers.append(peer)


    def _get_player(self, account_id):
        """
        Gets a player object from the DB if it exists. If not loads it from the db and saves it there.
        """

        player = self.session.query(Player).filter_by(accountId=account_id).first()
        if player:
            return player

        player = Player(accountId=account_id)
        player.load()

        return player



if __name__ == '__main__':
    session = get_session(drop_all=False)


    # player = Player(accountId=PLAYER_ID)
    # player.load()
    # session.add(player)
    # session.commit()

    player = session.query(Player).filter_by(accountId=PLAYER_ID).first()

    # loader = PeerLoader(player, session)
    # loader.load()

    session.commit()

    pass
