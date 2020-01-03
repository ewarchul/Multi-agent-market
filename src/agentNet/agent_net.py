import networkx as nx
import random
import matplotlib.pyplot as plt
import yaml
import network_utils  

class AgentNet(nx.Graph):
    """
    Class with agent network graph.
    """
    def __init__(self, init_num=2, net_type="complete", net_density="MEDIUM"):
        """
        Method initializes an agent network with default parameters.
        :param init_num: initial number of nodes for random graph construction algorithms or initial nodes for complete graph
        :param net_type: type of graph {"complete", "random", "custom"}
        :param net_density: density of random graph {SPARSE, MEDIUM, DENSE}
        """
        self.init_num =  init_num 
        self.net_type = net_type 
        self.net_density = net_density 
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
    def set_params(self, config_filename):
        """
        Method sets randomly a file link to agent policy for each agent id. 
        :param config_filename: path to file with links to policies
        """
        with open(config_filename, 'r') as configs:
            params_yaml = yaml.load(configs)
            self.agents_policies = {agent_id: random.choices(params_yaml.get('configs')) for agent_id in self.network.nodes}
    def add_agent(self, agent_id):
        """
        Method connects an agent with given id to randomly choosen agent from network. 
        :param agent_id: new agent id
        """
        sampled_agent = random.sample(list(self.network.nodes), 1)
        self.network.add_edge(agent_id, sampled_agent[0])
    def remove_agent(self, agent_id):
        """
        Method removes an agent from network. 
        :param agent_id: agent id choosen to be removed 
        """
        self.network.remove_node(agent_id)
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
        with open(filename, 'w') as network_file:
            yaml_network = yaml.load(network_file)
            self.init_num = yaml_network.get('agent_init_num', 2)
            self.net_type = yaml_network.get('network_type', "complete")
            self.net_density = yaml_network.get('network_density', "MEDIUM")
            self.agents_policies = yaml_network.get('agent_policies', None)
            self.connections = yaml_network.get('network_connections', None)

