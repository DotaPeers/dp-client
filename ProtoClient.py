import websockets
import asyncio
import json
import time
import base64

from proto import PeerData_pb2 as pdpb
from client.Player import Player, PlayerPeers


NBR = "12345"


async def loadPlayer(req: pdpb.PlayerRequest) -> pdpb.PlayerResponse:
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


async def loadPeers(req: pdpb.PeersRequest) -> pdpb.PeersResponse:
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


async def onMessage(ws, data):
    req = pdpb.PeerDataRequest()
    req.ParseFromString(base64.b64decode(data))
    print(req)
    resp = pdpb.PeerDataResponse()

    # Load the players
    for playerRequest in req.players:
        resp.players.append(
            await loadPlayer(playerRequest)
        )

    # Load the peers
    for peerRequest in req.peers:
        resp.peers.append(
            await loadPeers(peerRequest)
        )

    print(f"Len: {len(resp.SerializeToString())}")

    await ws.send(json.dumps({'type': 'proto_response', 'data': base64.b64encode(resp.SerializeToString()).decode()}))


async def receiveMessages():
    uri = 'ws://localhost:8000/ws/proto/' + NBR
    async with websockets.connect(uri, timeout=120) as ws:
        print('Waiting for messages')
        while True:
            resp = await ws.recv()
            await onMessage(ws, resp)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(receiveMessages())
