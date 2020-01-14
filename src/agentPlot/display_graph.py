import matplotlib.pyplot as plt
import networkx as nx
from agents.AgentBase import AgentBase
import logger
from agentNet.agent_net import AgentNet
from agents.Offer import Offer, OfferType
import numpy as np


def get_id(jid=''):
    jid = str(jid)
    return int(jid[len('agent_'):-(len(AgentBase.HOST) + 1)])


def normal_plot(graph, handlers, edge_colors, edge_labels, node_labels):
    """
    Plots graph
    :param graph: agent_net graph
    :param handlers: dictionary containing logs from the system
    :param edge_colors: list containing colors of edges
    :param edge_labels: list containing labels for edges
    :param node_labels: list containing labels for nodes
    """
    message = handlers.get(logger.EVENT_MESSAGE_SENT)
    status = handlers.get(logger.EVENT_AGENT_STATE_CHANGED)
    if status is not None:
        s = status[-1]
        node_labels[int(s.get('id'))-1] = "{}/{}".format(np.around(s.get('resource'), 2), np.around(s.get("money"), 2))

    if message is not None:
        s = message[-1]

        for num, edge in enumerate(graph.network.edges):
            if tuple(sorted((get_id(s.get('sender')) - 1, (get_id(s.get('receiver')) - 1)))) == edge:
                msg = s.get('content')
                edge_labels[edge] = "{}/{}".format(np.around(msg.money, 2), np.around(msg.resource, 2))

                if msg.type == OfferType.INITIAL_OFFER:
                    edge_colors[num] = "blue"
                elif msg.type == OfferType.COUNTER_OFFER:
                    edge_colors[num] = "yellow"
                elif msg.type == OfferType.ACCEPTING_OFFER:
                    edge_colors[num] = "green"
                elif msg.type == OfferType.BREAKDOWN_OFFER:
                    edge_colors[num] = "red"
                elif msg.type == OfferType.CONFIRMATION_OFFER:
                    edge_colors[num] = "green"
                else:
                    edge_colors[num] = "black"

    pos = nx.kamada_kawai_layout(graph.network)

    nx.draw_networkx_edges(graph.network, pos, edge_color=edge_colors)
    nx.draw_networkx_edge_labels(graph.network, pos, with_labels=True, edge_labels=edge_labels)
    nx.draw_networkx_nodes(graph.network, pos)
    nx.draw_networkx_labels(graph.network, pos, labels=node_labels)


def real_time_plot(graph, handlers):
    """
    Plots simulation graph in real time
    :param graph: agent_net graph
    :param handlers: dictionary containing logs from the system
    """
    global edge_colors
    edge_colors = ["black" for i in range(len(graph.network.edges))]
    global edge_labels
    edge_labels ={}
    for edge in graph.network.edges:
        edge_labels[edge] = '-/-'
    global node_labels
    node_labels = {}
    for node in graph.network.nodes:
        node_labels[node] = '-/-'
    plt.ion()
    plt.show()

    message = handlers.get(logger.EVENT_MESSAGE_SENT)
    status = handlers.get(logger.EVENT_AGENT_STATE_CHANGED)

    if message is not None:
        for s in message:
            for num, edge in enumerate(graph.network.edges):
                if tuple(sorted((get_id(s.get('sender')) - 1, (get_id(s.get('receiver')) - 1)))) == edge:
                    msg = s.get('content')
                    edge_labels[edge] = "{}/{}".format(np.around(msg.money, 2), np.around(msg.resource, 2))


                    if msg.type == OfferType.INITIAL_OFFER:
                        edge_colors[num] = "blue"
                    elif msg.type == OfferType.COUNTER_OFFER:
                        edge_colors[num] = "yellow"
                    elif msg.type == OfferType.ACCEPTING_OFFER:
                        edge_colors[num] = "green"
                    elif msg.type == OfferType.BREAKDOWN_OFFER:
                        edge_colors[num] = "red"
                    elif msg.type == OfferType.CONFIRMATION_OFFER:
                        edge_colors[num] = "green"
                    else:
                        edge_colors[num] = "black"

    if status is not None:
        for s in status:
            agent_id = s.get('id')
            node_labels[int(agent_id)-1] = "{}/{}".format(round(s.get('resource')), round(s.get("money")))
    while 1:
        normal_plot(graph, handlers, edge_colors, edge_labels, node_labels)
        plt.pause(0.0001)
        if not plt.fignum_exists(1):
            break
        plt.clf()


if __name__ == "main":
    graph = AgentNet(init_num=2, net_type='complete')
    graph.create_network()
    #
    global edge_colors
    edge_colors = ["black" for i in range(len(graph.network.edges))]
    global edge_labels
    edge_labels = {}
    global node_labels
    node_labels = {}
    for edge in graph.network.edges:
        edge_labels[edge] = '0/0'
    for node in graph.network.nodes:
        node_labels[node] = '50/50'


