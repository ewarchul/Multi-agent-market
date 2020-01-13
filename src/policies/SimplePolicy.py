from policies.policy import Policy
from agents.Offer import Offer, OfferType

import random


class SimplePolicy(Policy):
    """
    A simple policy
    """
    MAX_PRICE = 1000
    MIN_PRICE = 0.001

    def __init__(self, agent, minmal_price_change=0.1, *args):
        """
        Creates decision policy for given agent

        :param agent: The agent
        :param minmal_price_change: Minimal relative price change during negotiation
        :param args: Additional arguments
        """
        self.minimal_price_change=0.1
        super(SimplePolicy, self).__init__(agent, *args)

    def produce(self, limit):
        """
        :return: Value to produce, 0 if don't
        """

        actual_limit = min(limit, self.resource_increase_limit())

        if self.agent.config.production_cost:
            actual_limit = min(
                actual_limit,
                (self.agent.money_total - self.agent.money_in_use) / self.agent.config.production_cost)

        return actual_limit

    def drop_storage(self):
        """
        :return: Value of resource to drop, 0 if don't
        """
        return 0

    def initial_buy_offer(self):
        """
        :return: Initial buy offer or None if don't buy
        """
        if self.buy() and not self.agent.money_in_use:
            return Offer(
                OfferType.INITIAL_OFFER,
                is_sell_offer=False,
                resource=self.agent.current_needs,
                money=self.MIN_PRICE
            )
        else:
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
        if not self.buy():
            return Offer(OfferType.BREAKDOWN_OFFER, True, 0, 0)

        prev_offers = [oo for o in other_offers.values() for oo in o.other_offers]

        upper_resource_bound = max(o.resource for o in other_offers.values())\
            if prev_offers else self.resource_increase_limit()

        upper_price_bound = min(o.money / o.resource for o in other_offers.values())
        lower_price_bound = max(o.money / o.resource for o in prev_offers) if prev_offers else self.MIN_PRICE
        if own_offer:
            lower_price_bound = max(
                lower_price_bound,
                min((own_offer.money / own_offer.resource) * (1 + self.minimal_price_change), upper_resource_bound)
            )

        if self.agent.config.needs_satisfaction_cost:
            upper_price_bound = min(upper_price_bound, self.agent.config.needs_satisfaction_cost)
            lower_price_bound = min(lower_price_bound, self.agent.config.needs_satisfaction_cost)

        if self.agent.get_time_to_satisfy() < self.agent.get_timeout():
            lower_price_bound = upper_price_bound

        price = random.uniform(lower_price_bound, upper_price_bound)

        upper_resource_bound = min(upper_resource_bound, (
                self.agent.money_total - self.agent.money_in_use
                + (own_offer.money if own_offer else 0)
        ) / price)

        if upper_resource_bound == 0:
            return Offer(OfferType.BREAKDOWN_OFFER, False, 0, 0)
        return Offer(
            OfferType.COUNTER_OFFER,
            False,
            resource=upper_resource_bound,
            money=upper_resource_bound * price
        )

    def sell_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        prev_offers = [oo for o in other_offers.values() for oo in o.other_offers]

        upper_resource_bound = min(
            sum(o.resource for o in other_offers.values()),
            self.agent.resource_total - self.agent.resource_in_use + (own_offer.resource if own_offer else 0)
        )

        if upper_resource_bound == 0:
            return Offer(OfferType.BREAKDOWN_OFFER, False, 0, 0)

        lower_price_bound = max(o.money / o.resource for o in other_offers.values())
        upper_price_bound = min(o.money / o.resource for o in prev_offers) if prev_offers else self.MAX_PRICE
        if own_offer:
            upper_price_bound = min(
                upper_price_bound,
                max((own_offer.money / own_offer.resource) * (1 - self.minimal_price_change), lower_price_bound)
            )

        if self.agent.config.production_cost:
            lower_price_bound = self.agent.config.production_cost

        if upper_price_bound < lower_price_bound:
            return Offer(OfferType.BREAKDOWN_OFFER, False, 0, 0)

        price = random.uniform(lower_price_bound, upper_price_bound)
        resource = upper_resource_bound

        return Offer(OfferType.COUNTER_OFFER, is_sell_offer=True, money=price * resource, resource=resource)

    #################################
    # below are some helper methods #
    #################################

    def buy(self):
        return self.agent.current_needs and self.agent.money_total

    def resource_increase_limit(self):
        limit = self.agent.config.storage_limit - self.agent.resource_total + self.agent.current_needs

        return limit
