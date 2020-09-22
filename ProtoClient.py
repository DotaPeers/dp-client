import sys
import websockets
import asyncio
import json
import time
import base64
import threading

from proto import PeerData_pb2 as pdpb
from client.Player import Player, PlayerPeers


NBR = "12345"


class ProtoClient:
    """
    The client which connects to the DotaPeers Server to download data
    """

    def __init__(self, gui):
        self.gui = gui
        self.doRun = True

    def _log(self, data):
        """
        Logging function. Every print should be replaced by this method.
        This method logs to the console if the application is in console mode or the the console box if it's in GUI mode
        """

        if not self.gui:
            print(data)

        else:
            self.gui.addToTextBrowser(data)

    async def loadPlayer(self, req: pdpb.PlayerRequest) -> pdpb.PlayerResponse:
        player = pdpb.PlayerResponse(accountId=req.accountId)
        player_obj = Player(req.accountId)
        player_obj.load()

        player.username         = player_obj.username
        player.rank             = player_obj.rank.convertBack()
        player.dotaPlus         = player_obj.dotaPlus
        player.steamId          = player_obj.steamId
        player.avatars.small    = player_obj.avatars.small
        player.avatars.medium   = player_obj.avatars.medium
        player.avatars.large    = player_obj.avatars.large
        player.profileUrl       = player_obj.profileUrl
        player.countryCode      = player_obj.countryCode
        player.wins             = player_obj.wins
        player.loses            = player_obj.loses

        return player

    async def loadPeers(self, req: pdpb.PeersRequest) -> pdpb.PeersResponse:
        peers = pdpb.PeersResponse(accountId=req.accountId)
        peers_obj = PlayerPeers(req.accountId)
        peers_obj.load()

        for peer_obj in peers_obj.peers:
            peer = pdpb.Peer()
            peer.accountId2 = peer_obj.accountId2
            peer.games      = peer_obj.games
            peer.wins       = peer_obj.games

            peers.peers.append(peer)

        return peers

    async def parseMeta(self, req: pdpb.Metadata) -> None:
        if req.start:
            self._log("Starting download...")

        if req.end:
            self._log("Finished download...")

    async def onMessage(self, ws, data):
        req = pdpb.PeerDataRequest()
        req.ParseFromString(base64.b64decode(data))
        resp = pdpb.PeerDataResponse()

        self._log(req)

        # Parses the metadata
        await self.parseMeta(req.metadata)

        # Load the players
        for playerRequest in req.players:
            resp.players.append(
                await self.loadPlayer(playerRequest)
            )

        # Load the peers
        for peerRequest in req.peers:
            resp.peers.append(
                await self.loadPeers(peerRequest)
            )

        self._log(f"Len: {len(resp.SerializeToString())}")

        await ws.send(json.dumps({'type': 'proto_response', 'data': base64.b64encode(resp.SerializeToString()).decode()}))

    async def receiveMessages(self, id):
        uri = 'ws://localhost:8000/ws/proto/' + id
        self._log(f"Connecting to {uri}...")

        try:
            async with websockets.connect(uri, timeout=120) as ws:
                self._log("Connected.")

                while self.doRun:
                    resp = await ws.recv()
                    await self.onMessage(ws, resp)

                self._log("Closed connection.")

        # Raised when the Client can't connect to the server because it's not running
        except websockets.InvalidMessage as e1:
            if 'did not receive a valid HTTP response' in str(e1):
                self._log("️Failed to connect to the server!")
            raise e1


if __name__ == '__main__':
    client = ProtoClient(None)
    asyncio.get_event_loop().run_until_complete(client.receiveMessages(NBR))
