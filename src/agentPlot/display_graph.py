import matplotlib.pyplot as plt
import networkx as nx
from agents.AgentBase import AgentBase
import logger
from agentNet.agent_net import AgentNet
from agents.Offer import Offer, OfferType
import numpy as np
import queue


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
        print("----------------", status)

        while not status.empty():
            stats = status.get()
            print("fffff", stats)
            node_labels[int(stats.get('id'))] = "({}){}/{}".format(stats.get('id'), np.around(stats.get('resource'), 2),
                                                                   np.around(stats.get("money"), 2))
        print(node_labels)
    if message is not None:
        print("hhhhhhhhhhhhhhhhhhhh")

        print("----------------", message)

        while not message.empty():
            s = message.get()
            for num, edge in enumerate(graph.network.edges):
                if tuple(sorted((get_id(s.get('sender')), (get_id(s.get('receiver')))))) == edge:
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
    edge_labels = {}
    for edge in graph.network.edges:
        edge_labels[edge] = '-/-'
    global node_labels
    node_labels = {}
    for node in graph.network.nodes:
        node_labels[node] = '({})-/-'.format(node + 1)
    plt.ion()
    plt.show()

    message = handlers.get(logger.EVENT_MESSAGE_SENT)
    status = handlers.get(logger.EVENT_AGENT_STATE_CHANGED)

    if message is not None:
        while not message.empty():
            for num, edge in enumerate(graph.network.edges):
                if tuple(
                        sorted((get_id(message.get().get('sender')), (get_id(message.get().get('receiver')))))) == edge:
                    msg = message.get().get('content')
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
        print(status)
        while not status.empty():
            agent_id = status.get().get('id')
            node_labels[int(agent_id) - 1] = "({}){}/{}".format(status.get().get('id'),
                                                                round(status.get().get('resource')),
                                                                round(status.get().get("money")))
    while 1:
        normal_plot(graph, handlers, edge_colors, edge_labels, node_labels)
        plt.pause(AgentBase.TIME_QUANT * 10)
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


