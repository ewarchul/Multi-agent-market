from agents.Agent import Agent
from config import AgentConfig, const, random_uniform
from policies import LazyPolicy, SimplePolicy
from run import disable_spade_warnings
from agentNet.agent_net import AgentNet

import logger
from pprint import pprint
import time

from agentPlot.display_graph import real_time_plot

graph = AgentNet(init_num=2, net_type='complete')
graph.create_network()

global eventDict
eventDict = {}


def handler(event, **kwargs):
    # print("hello")
    if event in eventDict.keys():
        eventDict[event].append(kwargs)
    else:
        eventDict[event] = []
        eventDict[event].append(kwargs)


disable_spade_warnings()
logger.initialize_default_logger(None)

logger.logger.register_event_handler(logger.EVENT_AGENT_STATE_CHANGED, handler)
logger.logger.register_event_handler(logger.EVENT_MESSAGE_SENT, handler)

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

    time.sleep(10)

pprint(eventDict)
real_time_plot(graph, eventDict)