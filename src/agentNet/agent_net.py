import networkx as nx
import itertools
import random
import matplotlib.pyplot as plt
import yaml
from agentNet.network_utils import *

class AgentNet(object):
    """
    Class with agent network graph.
    """
    def __init__(self, init_num=2, net_type="custom", net_density="MEDIUM", network=None, agents_policies=None, connections = None):
        """
        Method initializes an agent network with default parameters.
        :param init_num: initial number of nodes for random graph construction algorithms or initial nodes for complete graph
        :param net_type: type of graph {"complete", "random", "custom"}
        :param net_density: density of random graph {SPARSE, MEDIUM, DENSE}
        :param network: field which contains networkx's graph 
        :param agents_policies: map from agent id to file name with agent policy
        :param connections: map with nodes connections 
        """
        super(AgentNet, self).__init__()
        self.init_num =  init_num 
        self.net_type = net_type 
        self.net_density = net_density 
        self.network = network  
        self.agents_policies = agents_policies 
        self.connections = connections
    def create_network(self):
        """
        Method creates an agent network up to net_type.
        """
        if self.net_type == "complete":
            self.network = nx.complete_graph(n = self.init_num)
        elif self.net_type == "custom":
            self.network = nx.Graph(self.connections)
        else:
            self.network = nx.fast_gnp_random_graph(self.init_num, dens2prob(self.net_density))
    def set_policies(self, config_filename):
        """
        Method sets policies from config file. 
        :param config_filename: path to file with policies config
        """
        with open(config_filename, 'r') as configs:
            params_yaml = yaml.load(configs)
            if self.agents_policies:
                self.agents_policies.update(params_yaml['agents_policies'])
            else:
                self.agents_policies = params_yaml['agents_policies'] 
    def set_policy(self, agent_ids, policies):
        """
        Method sets policies for given agents ids by user.
        :param agent_ids: list of ids
        :param policies: list of policies
        """
        if self.agents_policies:
            self.agents_policies.update({agent_id: policy for (agent_id, policy) in list(zip(agent_ids, policies))})
        else:
            self.agents_policies = {agent_id: policy for (agent_id, policy) in list(zip(agent_ids, policies))}
    def set_connections(self, config_filename):
        """
        Method sets connections from config file. 
        :param config_filename: path to file with connections config
        """
        with open(config_filename, 'r') as configs:
            params_yaml = yaml.load(configs)
            if self.network is None:
                self.connections = params_yaml['network_connections'] 
            else:
                self.network = nx.compose(self.network, nx.Graph(params_yaml['network_connections']))
    def set_connection(self, agent_id, ids_list):
        """
        Method connects an agent with given id to choosen agents from network.
        If list of choosen agents is empty then method connects an agent
        with given id to randomly choosen agent from network. 
        :param agent_id: new agent id
        :param ids_list: list of ids in network
        """
        if ids_list:
            self.network.add_edges_from([(agent_id, id) for id in ids_list])
        else:
            sampled_agent = random.sample(list(self.network.nodes), 1)
            self.network.add_edge(agent_id, sampled_agent[0])
    def remove_connection(self, agent_ids):
        """
        Method removes an agent from network. 
        :param agent_id: agent id(s) choosen to be removed 
        :type agent_id: list
        """
        self.network.remove_nodes_from(agent_ids)
    def show_network(self):
        """
        Method plots graph with connections (edges) between agents (nodes). 
        """
        nx.draw_networkx(self.network)
        plt.show()
    def save_network(self, filename):
        """
        Method saves agent network to YAML file.
        :param filename: destination filename
        """
        with open(filename, 'w') as yaml_file:
            yaml.dump({
                    'network_type': self.net_type,
                    'network_density': self.net_density,
                    'agent_init_num': self.init_num,
                    'network_connections': get_connections(self.network),
                    'agents_policies': self.agents_policies
            }, yaml_file, default_flow_style=False)
    def load_network(self, filename):
        """
        Method reads agents network from YAML file.
        :param filename: source filename
        """
        with open(filename, 'r') as network_file:
            yaml_network = yaml.load(network_file)
            self.init_num = yaml_network.get('agent_init_num', 2)
            self.net_type = yaml_network.get('network_type', "complete")
            self.net_density = yaml_network.get('network_density', "MEDIUM")
            self.agents_policies = yaml_network.get('agents_policies', None)
            self.connections = yaml_network.get('network_connections', None)

