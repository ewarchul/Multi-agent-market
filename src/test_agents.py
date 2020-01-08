from agents.AgentBase import AgentBase
from config import AgentConfig
from agents.Offer import Offer, OfferType

import logger

import time


class Agent(AgentBase):
    def __init__(self, id, connections):
        config = AgentConfig()
        super(Agent, self).__init__(id, connections, config)

    def get_counter_offer(self, offer, sender_offers):
        selling = not list(sender_offers.values())[0].is_sell_offer
        return Offer(OfferType.BREAKDOWN_OFFER if selling else OfferType.COUNTER_OFFER, selling, 0, 0)

    def get_timeout(self):
        return 100

    def get_initial_sell_offer(self):
        return Offer(OfferType.INITAL_OFFER, True, 100, 200)

    def check_accepted(self, offer, sender_offers):
        return None

    def accepted_offers(self, offer, sender_offers):
        pass


logger.initialize_default_logger(None)
a1 = Agent(1, [2])
a2 = Agent(2, [1])

a1.start()
a2.start()

time.sleep(10)

a1.run_transaction_in_server_mode(True)

