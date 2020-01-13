from policies.policy import Policy
from agents.Offer import Offer, OfferType


class LazyPolicy(Policy):
    """
    A policy to do nothing
    """
    def __init__(self, agent, *args):
        """
        Creates decision policy for given agent

        :param agent: The agent
        :param args: Additional arguments
        """
        super(LazyPolicy, self).__init__(agent, *args)

    def produce(self, limit):
        """
        :return: Value to produce, 0 if don't
        """
        return 0

    def drop_storage(self):
        """
        :return: Value of resource to drop, 0 if don't
        """
        return 0

    def initial_buy_offer(self):
        """
        :return: Initial buy offer or None if don't buy
        """
        return None

    def initial_sell_offer(self):
        """
        :return: Initial sell offer or None if don't sell
        """
        return None

    def buy_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        return Offer(OfferType.BREAKDOWN_OFFER, True, 0, 0)

    def sell_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        return Offer(OfferType.BREAKDOWN_OFFER, False, 0, 0)
