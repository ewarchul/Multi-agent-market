from agents.Agent import Agent
from config import AgentConfig, const, random_uniform
from policies import LazyPolicy

import logger

import time


logger.initialize_default_logger(None)

conf1 = AgentConfig()
conf2 = AgentConfig()

conf1._income = const
conf1._income_args = [3]
conf1.income_time = 5
conf1._policy_builder = LazyPolicy

conf2.initial_money = 10
conf2.needs_satisfaction_timeout = 3
conf2._needs = random_uniform
conf2._needs_args = [3, 4]
conf2.needs_satisfaction_cost = 0.5
conf2._policy_builder = LazyPolicy

a1 = Agent(1, [2], conf1)
a2 = Agent(2, [1], conf2)

a1.start()
a2.start()

time.sleep(10)

