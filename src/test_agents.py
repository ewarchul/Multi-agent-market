from agents.Agent import Agent
from config import AgentConfig
from agents.Offer import Offer, OfferType

import logger

import time


logger.initialize_default_logger(None)
a1 = Agent(1, [2], AgentConfig())
a2 = Agent(2, [1], AgentConfig())

a1.start()
a2.start()

time.sleep(10)

a1.run_transaction_in_server_mode(True)

