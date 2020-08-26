import networkx as nx
import plotly.graph_objs as go
from fa2 import ForceAtlas2
from fa2l import force_atlas2_layout
import random
from PIL import Image
import matplotlib.pyplot as plt
import math

from pyvis.network import Network

import pandas as pd
from colour import Color

from database.database import get_session
from database.models import *

# import the css template, and pass the css template into dash
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app.title = "Transaction Network"
#
# YEAR = [2010, 2019]
# ACCOUNT = "A0001"


def plotlyCode():
    # -----  Generation of the visible parts  -----

    traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
    colors = list(Color('lightcoral').range_to(Color('darkred'), len(G.edges())))
    colors = ['rgb' + str(x.rgb) for x in colors]

    # --- Add the lines between the nodes ---
    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        weight = float(0.1) * 10
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': weight},  # Thickness
                           marker=dict(color=colors[index]),
                           line_shape='spline',
                           opacity=1)
        # Adds the lines between the nodes (but not the arrows)
        traceRecode.append(trace)
        index = index + 1

    # --- Creates the Nodes ---

    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'color': 'LightSkyBlue'})

    # --- Adds the hover text to the lines between the nodes ---

    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'},
                                    opacity=0)

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        hovertext = 'Hovertext 2'
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    # Hover text for the lines
    traceRecode.append(middle_hover_trace)

    layout = go.Layout(title='Interactive Transaction Visualization', showlegend=False, hovermode='closest',
                       margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                       xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                       yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                       height=800,
                       clickmode='event+select',
                       )

    index = 0
    images = list()
    for node in G.nodes():
        node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                                hoverinfo="text", opacity=1)

        x, y = G.nodes[node]['pos']
        # Hovertext on the node
        hovertext = 'Hovertext: ' + node
        text = node  # Username
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        node_trace.marker.size = 2  # Size of the marker
        index = index + 1

        # Profile picture generation
        size = random.randint(100, 400) / 100
        images.append(
            {'x': x - (size / 2), 'y': y + (size / 2), 'xref': 'x', 'yref': 'y', 'sizex': size, 'sizey': size,
             'source': Image.open('profile.png')}
        )

        # Adds the nodes to the graph
        traceRecode.append(node_trace)

    figure = go.Figure(data=traceRecode, layout=layout)

    for img in images:
        figure.add_layout_image(img)

    # Configure axes
    figure.update_xaxes(
        visible=True,
    )

    figure.update_yaxes(
        visible=False,
        # the scaleanchor attribute ensures that the aspect ratio stays constant
        scaleanchor="x"
    )

    return figure


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


def _getEdges(G: nx.Graph, player, depth=0, parent=None):

    for p in player.peers:
        p1 = p.player1.username
        p2 = p.player2.username

        if p1 not in G.nodes:
            G.add_node(p1, size=_gamesToNodeSize(p.player1.games), shape='image', image='{}/{}.png'.format(Config.PROFILE_PICTURES_FOLDER, p.player1.accountId))

        if p2 not in G.nodes:
            G.add_node(p2, size=_gamesToNodeSize(p.player2.games), shape='image', image='{}/{}.png'.format(Config.PROFILE_PICTURES_FOLDER, p.player2.accountId))

        if not G.has_edge(p1, p2) and not G.has_edge(p2, p1):
            G.add_edge(p1, p2, weight=_gamesToEdgeWeight(p.games), value=_gamesToEdgeValue(p.games))

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

