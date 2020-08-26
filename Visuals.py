import networkx as nx
from fa2 import ForceAtlas2
from fa2l import force_atlas2_layout
import random
from PIL import Image
import matplotlib.pyplot as plt
import math

from pyvis.network import Network

import pandas as pd

from database.database import get_session
from database.models import *


def getTestGraph():
    edge1 = pd.read_csv('edge1.csv')
    node1 = pd.read_csv('node1.csv')

    accountSet = set()  # contain unique account
    for index in range(0, len(edge1)):
        accountSet.add(edge1['Source'][index])
        accountSet.add(edge1['Target'][index])

    G = nx.from_pandas_edgelist(edge1, 'Source', 'Target', ['Source', 'Target', 'TransactionAmt', 'Date'],
                                create_using=nx.MultiDiGraph())

    # Add specific data to a node
    nx.set_node_attributes(G, node1.set_index('Account')['CustomerName'].to_dict(), 'CustomerName')
    nx.set_node_attributes(G, node1.set_index('Account')['Type'].to_dict(), 'Type')

    return G


def __linearGamesToSize(games: int):
    size = games / 100

    if size < 20:
        return 10

    elif size > 100:
        return 50

    return size


def __sigmoidGamesToSize(games: int):
    streckungY   = 28
    streckungX   = 40
    rechtsShift  = 1.2
    upshift      = 5
    gamesDivisor = 100

    return streckungY * math.tanh((games / gamesDivisor / streckungX) - rechtsShift) + streckungY + upshift


def _gamesToNodeSize(games: int):
    return __sigmoidGamesToSize(games)


def _gamesToEdgeWeight(games: int):
    return games / 1


def _gamesToEdgeValue(games: int):
    return games / 100


def _addNode(G, player):
    G.add_node(player.username,
               size=_gamesToNodeSize(player.games),
               shape='image',
               image='{}/{}.png'.format(Config.PROFILE_PICTURES_FOLDER, player.accountId),
               title="Username: {} <br> County: {} <br>Games: {} <br>Wins: {} <br>Loses: {} <br>Winrate: {} <br>Rank: {}".format(player.username, player.countryCode, player.games, player.wins, player.loses, player.winrate, player.rank.toStr()),
               )


def _addEdge(G, player: Player, peer: Peer):
    player1 = player
    player2 = peer.otherPlayer(player)

    G.add_edge(player1.username, player2.username,
               weight=_gamesToEdgeWeight(peer.games),
               value=_gamesToEdgeValue(peer.games),
               title='{} -> {} <br>Games: {} <br>Wins: {} <br>Loses: {} <br>Winrate: {}'.format(player1.username, player2.username, peer.games, peer.wins, peer.loses, peer.winrate),
               )


def _getEdges(G: nx.Graph, player, depth=0, parent=None):

    for p in player.peers:
        p1 = p.player1.username
        p2 = p.player2.username

        if p1 not in G.nodes:
            _addNode(G, p.player1)

        if p2 not in G.nodes:
            _addNode(G, p.player2)

        if not G.has_edge(p1, p2) and not G.has_edge(p2, p1):
            _addEdge(G, player, p)

        if depth < Config.MAX_RECURSION_DEPTH:
             _getEdges(G, p.otherPlayer(player), depth=depth + 1, parent=player)


def getPlayerGraph():
    G = nx.Graph()

    session = get_session()
    player = session.query(Player).filter_by(accountId=154605920).first()

    _getEdges(G, player, depth=0, parent=None)

    return G


def network_graph():

    G = getPlayerGraph()

    # Generate the positions of the nodes
    forceatlas2 = ForceAtlas2(
                              outboundAttractionDistribution=True,  # Distributes attraction along outbound edges. Hubs attract less and thus are pushed to the borders
                              edgeWeightInfluence=1,  # How much influence you give to the edges weight. 0 is "no influence" and 1 is "normal"

                              # Performance
                              jitterTolerance=0.8,  # How much swinging you allow. Above 1 discouraged. Lower gives less speed and more precision
                              barnesHutOptimize=True,   # Barnes Hut optimization, n2 complexity to n.ln(n)
                              barnesHutTheta=1,

                              # Tuning
                              scalingRatio=0.5, # How much repulsion you want. More makes a more sparse graph (spärlich)
                              strongGravityMode=False,  # A stronger gravity view
                              gravity=0.4,  # Attracts nodes to the center. Prevents islands from drifting away

                              # Log
                              verbose=True
                              )
    pos = forceatlas2.forceatlas2_networkx_layout(G, iterations=10000)

    # Add the generated positions to the nodes
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])
    return G, pos


if __name__ == '__main__':

    G, pos = network_graph()

    nt = Network(height='90%', width='90%')
    nt.from_nx(G)

    nt.toggle_physics(False)
    nt.show('nt.html')

