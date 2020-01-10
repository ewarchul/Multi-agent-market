from agents.AgentBase import AgentBase


class Agent(AgentBase):
    def __init__(self, agent_id, connections, config):
        super(Agent, self).__init__(agent_id, connections, config)
