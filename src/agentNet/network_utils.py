import enum

class DensityProb(enum.Enum):
        SPARSE = 0.1
        MEDIUM = 0.5
        DENSE = 0.8
def dens2prob(dens_name):
        """
        Enum class utility to get the value of given density name.
        :param dens_name: name of density 
        :type dens_name: enum 'DensityProb'
        """
        return DensityProb[dens_name].value
def get_connections(network):
    """
    Function creates a dictionary with agent id's as a key and adjacent nodes as a value.
    :param network: object of graph
    :type network: networkx.classes.graph.Graph 
    """
    return {agent_id: list(adj_agents.keys()) for (agent_id, adj_agents) in network.adjacency()}


