from time import sleep

import matplotlib.pyplot as plt
import networkx as nx


def normal_plot(graph, handlers, edge_colors, edge_labels, node_labels):

    offer = handlers.get("EVENT_OFFER")
    accept = handlers.get("EVENT_ACCEPTED")
    drop = handlers.get("EVENT_NEGOTIATION_BREAKDOWN")
    coffer = handlers.get("EVENT_CANTEROFFER")

    status = handlers.get("EVENT_RES_CHANGED")
    s = status[-1]
    node_labels[s.get('agent')] = "{}/{}".format(s.get('resource'), s.get("money"))
    print(edge_labels)
    s = offer[-1]
    for num, edge in enumerate(graph.network.edges):
        print(tuple(sorted((s.get('agent'), s.get('receiver')))))
        if tuple(sorted((s.get('agent'), s.get('receiver')))) == edge:
            print("hi")
            edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
            edge_colors[num] = "blue"
            print(edge_labels)
    s = accept[-1]
    for num, edge in enumerate(graph.network.edges):
        if tuple(sorted((s.get('agent'), s.get('receiver')))) == edge:
            edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
            edge_colors[num] = "green"
    s = drop[-1]
    for num, edge in enumerate(graph.network.edges):
        if tuple(sorted((s.get('agent'), s.get('receiver')))) == edge:
            edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
            edge_colors[num] = "red"
    s = coffer[-1]
    for num, edge in enumerate(graph.network.edges):
        if tuple(sorted((s.get('agent'), s.get('receiver')))) == edge:
            edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
            edge_colors[num] = "yellow"

    pos = nx.kamada_kawai_layout(graph.network)

    nx.draw_networkx_edges(graph.network, pos, edge_color=edge_colors)
    nx.draw_networkx_edge_labels(graph.network, pos, with_labels=True, edge_labels=edge_labels)
    nx.draw_networkx_nodes(graph.network, pos)
    nx.draw_networkx_labels(graph.network, pos, labels=node_labels)


def real_time_plot(graph, handlers):
    # TODO: zmiana koloru krawedzi jak pojawia sie tranzakcja - info jaka byla tranzakcja
    # to wszystko z logera bedzie brane chyba
    # TODO: label z ilością  zasobów które ma agent - trzeba to skads brac
    #handlers = log.handlers
    global edge_colors

    global edge_labels

    global node_labels

    plt.ion()
    plt.show()
    offer = handlers.get("EVENT_OFFER")
    accept = handlers.get("EVENT_ACCEPTED")
    drop = handlers.get("EVENT_NEGOTIATION_BREAKDOWN")
    coffer = handlers.get("EVENT_CANTEROFFER")
    status = handlers.get("EVENT_RES_CHANGED")

    for s in offer:
        print("hello")
        print(s)
        for num, edge in enumerate(graph.network.edges):
            print(tuple(sorted((s.get('agent'), s.get('receiver')))))
            if tuple(sorted((s.get('agent'), s.get('receiver'))))== edge:
                print("hi")
                edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
                edge_colors[num] = "blue"
                print(edge_labels)

    for s in accept:
        for num, edge in enumerate(graph.network.edges):
            if tuple(sorted((s.get('agent'), s.get('receiver')))) == edge:
                edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
                edge_colors[num] = "green"

    for s in drop:
        for num, edge in enumerate(graph.network.edges):
            if tuple(sorted((s.get('agent'), s.get('receiver'))))== edge:

                edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
                edge_colors[num] = "red"

    for s in coffer:
        for num, edge in enumerate(graph.network.edges):
            if tuple(sorted((s.get('agent'), s.get('receiver')))) == edge:
                edge_labels[edge] = "{}/{}".format(s.get('resource'), s.get("money"))
                edge_colors[num] = "yellow"

    for s in status:
        print(s)
        node_labels[s.get('agent')] = "{}/{}".format(s.get('resource'), s.get("money"))
        print(node_labels)
    while 1:
        print("ohoho")
        print(edge_labels)
        #handlers = log.handlers
        normal_plot(graph, handlers, edge_colors, edge_labels, node_labels)
        plt.pause(0.01)
        if not plt.fignum_exists(1):
            break
        plt.clf()


graph = AgentNet(agent_num=8)
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
l = ["black" for i in range(10)]

handlers = {"EVENT_RES_CHANGED": [{"agent": 1, "resource": 10, "money": 20}, {"agent": 3, "resource": 60, "money": 22}, {"agent": 5, "resource": 30, "money": 50}], "EVENT_OFFER": [{"agent": 1, 'receiver': 5, "resource": 30, "money": 50}], "EVENT_CANTEROFFER": [{"agent": 2, 'receiver': 3, "resource": 3, "money": 500}], "EVENT_NEGOTIATION_BREAKDOWN": [{"agent": 2, 'receiver': 1, "resource": 40, "money": 22}], "EVENT_ACCEPTED": [{"agent": 3, 'receiver': 6, "resource": 330, "money": 5}]}

real_time_plot(graph, handlers)
print(edge_colors)
handlers = {"EVENT_RES_CHANGED": [{"agent": 1, "resource": 10, "money": 20}, {"agent": 3, "resource": 60, "money": 22}, {"agent": 5, "resource": 30, "money": 50}], "EVENT_OFFER": [{"agent": 1, 'receiver': 5, "resource": 30, "money": 50}], "EVENT_CANTEROFFER": [{"agent": 2, 'receiver': 3, "resource": 3, "money": 500}], "EVENT_NEGOTIATION_BREAKDOWN": [{"agent": 2, 'receiver': 1, "resource": 40, "money": 22}], "EVENT_ACCEPTED": [{"agent": 2, 'receiver': 6, "resource": 330, "money": 7}]}

real_time_plot(graph, handlers)