import networkx as nx
import random
import matplotlib.pyplot as plt
import enum

class DensityProb(enum.Enum):
        SPARSE = 0.1
        MEDIUM = 0.5
        DENSE = 0.8
def dens2prob(dens_name):
            return DensityProb[dens_name].value

class AgentNet(object):
    """
    Class with agent network graph.
    """
    def __init__(self, agent_num=None, net_type=None, net_density=None):
        self.agent_num =  agent_num if agent_num is not None else 2
        self.net_type = net_type if net_type is not None else 0
        self.net_density = net_density if net_density is not None else "MEDIUM"
    def create_network(self):
        if self.net_type == 0:
            self.network = nx.complete_graph(n = self.agent_num)
        else:
            self.network = nx.fast_gnp_random_graph(self.agent_num, dens2prob(self.net_density))
    def add_agent(self, agent_id):
       sampled_agent = random.sample(list(self.network.nodes), 1) 
       self.network.add_edge(agent_id, sampled_agent[0])
    def remove_agent(self, agent_id):
        self.network.remove_node(agent_id)
    def show_network(self):
        nx.draw_networkx(self.network)
        plt.show()
    def save_network(self, filename):
        nx.write_yaml(self.network,  filename)
    def load_network(self):
        nx.read_yaml(self.network, filename)
