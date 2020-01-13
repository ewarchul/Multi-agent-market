from agents.Agent import Agent
from config import AgentConfig, const, random_uniform
from policies import LazyPolicy, SimplePolicy
from run import disable_spade_warnings, visualisation
from agentNet.agent_net import AgentNet


import logger
from pprint import pprint
import time

graph = AgentNet(init_num=2, net_type='complete')
graph.create_network()

disable_spade_warnings()
f = open('log2.csv', 'w+')
logger.initialize_default_logger(f)

conf1 = AgentConfig()
conf2 = AgentConfig()

conf1.initial_resource = 100
conf1.storage_limit = 100
conf1._policy_builder = SimplePolicy
conf1._policy_builder_args = [0.1, 2, 2, 0.01, 0.01]

conf2.initial_money = 10
conf2.needs_satisfaction_timeout = 5
conf2._needs = random_uniform
conf2._needs_args = [3, 4]
conf2.needs_satisfaction_cost = 0.5
conf2._policy_builder = SimplePolicy
conf2._policy_builder_args = [0.1, 2, 2, 0.01, 0.01]


if __name__ == '__main__':
    a1 = Agent(1, [2], conf1)
    a2 = Agent(2, [1], conf2)

    a1.start()
    a2.start()
    visualisation(graph, logger)
    time.sleep(10)


