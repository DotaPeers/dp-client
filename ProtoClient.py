import websockets
import asyncio
import json
import time
import base64

from proto import PeerData_pb2 as pdpb
from client.Player import Player


NBR = "12345"


async def onMessage(ws, data):
    req = pdpb.PeerDataRequest()
    req.ParseFromString(base64.b64decode(data))
    print(req)

    resp = pdpb.PeerDataResponse()
    for p in req.players:
        player = pdpb.PlayerResponse(accountId=p.accountId)
        player_obj = Player(accountId=p.accountId)
        player_obj.load()

        player.username = player_obj.username
        player.rank = player_obj.rank.convertBack()
        player.dotaPlus = player_obj.dotaPlus
        player.steamId = player_obj.steamId
        player.avatars.small = player_obj.avatars.small
        player.avatars.medium = player_obj.avatars.medium
        player.avatars.large = player_obj.avatars.large
        player.profileUrl = player_obj.profileUrl
        player.countryCode = player_obj.countryCode
        player.wins = player_obj.wins
        player.loses = player_obj.loses

        for peer in player_obj.peers:
            peer_obj = pdpb.Peer()
            peer_obj.accountId1 = peer.player1
            peer_obj.accountId2 = peer.player2
            peer_obj.wins = peer.wins
            peer_obj.loses = peer.loses
            player.peers.append(peer_obj)

        player.timestamp = int(player_obj.timestamp.timestamp())

        resp.players.append(player)

    await ws.send(json.dumps({'type': 'proto_response', 'data': base64.b64encode(resp.SerializeToString()).decode()}))


async def receiveMessages():
    uri = 'ws://localhost:8000/ws/proto/' + NBR
    async with websockets.connect(uri) as ws:
        print('Waiting for messages')
        while True:
            resp = await ws.recv()
            await onMessage(ws, resp)

asyncio.get_event_loop().run_until_complete(receiveMessages())
