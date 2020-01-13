class Policy(object):
    """
    Policy base class
    """
    def __init__(self, agent, *args):
        """
        Creates decision policy for given agent

        :param agent: The agent
        :param args: Additional arguments
        """
        self.agent = agent

    def produce(self, limit):
        """
        :return: Value to produce, 0 if don't
        """
        raise NotImplementedError

    def drop_storage(self):
        """
        :return: Value of resource to drop, 0 if don't
        """
        raise NotImplementedError

    def initial_buy_offer(self):
        """
        :return: Initial buy offer or None if don't buy
        """
        raise NotImplementedError

    def initial_sell_offer(self):
        """
        :return: Initial sell offer or None if don't sell
        """
        raise NotImplementedError

    def buy_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        raise NotImplementedError

    def sell_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        raise NotImplementedError

    def register_successful(self, offer):
        raise NotImplementedError
