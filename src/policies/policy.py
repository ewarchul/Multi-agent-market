class Policy(object):
    """
    Policy base class

    TODO method arguments and return types specification
    """
    def __init__(self, agent, *args):
        """
        Creates decision policy for given agent

        :param agent: The agent
        :param args: Additional arguments
        """
        self.agent = agent

    def produce(self, *args, **kwargs):
        raise NotImplementedError

    def drop_storage(self, *args, **kwargs):
        raise NotImplementedError

    def initial_buy_offer(self, *args, **kwargs):
        raise NotImplementedError

    def initial_sell_offer(self, *args, **kwargs):
        raise NotImplementedError

    def buy_counter_offer(self, *args, **kwargs):
        raise NotImplementedError

    def sell_counter_offer(self, *args, **kwargs):
        raise NotImplementedError
