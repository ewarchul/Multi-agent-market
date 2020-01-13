from policies.policy import Policy
from agents.Offer import Offer, OfferType

import random


class SimplePolicy(Policy):
    """
    A simple policy
    """
    MAX_PRICE = 1000
    MIN_PRICE = 0.001
    MIN_RESOURCE = 0.001

    def __init__(self, agent, minimal_price_change=0.1, buy_if_has_money_prob=0, sell_if_has_resource_prob=0, *args):
        """
        Creates decision policy for given agent

        :param agent: The agent
        :param minmal_price_change: Minimal relative price change during negotiation
        :param buy_if_has_money: probability of making initial buy offer if has no needs but has money
        :param sell_if_has_resource_prob: probability of making initial sell offer if has resource
        :param args: Additional arguments
        """
        self.ACCURACY = agent.ACCURACY
        self.minimal_price_change = minimal_price_change
        self.buy_if_has_money_prob = buy_if_has_money_prob
        self.sell_if_has_money_prob = sell_if_has_resource_prob
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

        return round(actual_limit, self.ACCURACY)

    def drop_storage(self):
        """
        :return: Value of resource to drop, 0 if don't
        """
        return 0

    def initial_buy_offer(self):
        """
        :return: Initial buy offer or None if don't buy
        """
        if self.agent.money_total and not self.agent.money_in_use and not self.agent.resource_in_use:
            if self.agent.current_needs:
                return Offer(
                    OfferType.INITIAL_OFFER,
                    is_sell_offer=False,
                    resource=self.agent.current_needs,
                    money=self.MIN_PRICE
                )
            elif self.buy_if_has_money_prob and self.agent.resource_total < self.agent.config.storage_limit\
                    and random.random() < self.buy_if_has_money_prob:
                return Offer(
                    OfferType.INITIAL_OFFER,
                    is_sell_offer=False,
                    resource=self.random(
                        self.MIN_RESOURCE,
                        self.agent.config.storage_limit - self.agent.resource_total),
                    money=self.MIN_PRICE
                )
        else:
            return None

    def initial_sell_offer(self):
        """
        :return: Initial sell offer or None if don't sell
        """
        if self.agent.resource_total and not self.agent.resource_in_use and not self.agent.money_in_use\
                and random.random() < self.sell_if_has_money_prob:
            return Offer(
                OfferType.INITIAL_OFFER,
                is_sell_offer=True,
                resource=self.random(
                    self.MIN_RESOURCE,
                    self.agent.resource_total),
                money=self.MAX_PRICE
            )

    def buy_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        if not self.agent.money_total - self.agent.money_in_use:
            return Offer(OfferType.BREAKDOWN_OFFER, False, 0, 0)

        prev_offers = [oo for o in other_offers.values() for oo in o.other_offers if oo.resource]
        other_offers = [o for o in other_offers.values() if o.resource]

        upper_resource_bound = sum(o.resource for o in other_offers)\
            if other_offers else self.resource_increase_limit()

        upper_price_bound = min(o.money / o.resource for o in other_offers)
        lower_price_bound = max(o.money / o.resource for o in prev_offers) if prev_offers else self.MIN_PRICE
        if own_offer:
            lower_price_bound = max(
                lower_price_bound,
                min((own_offer.money / own_offer.resource) * (1 + self.minimal_price_change), upper_resource_bound)
            )

        if self.agent.config.needs_satisfaction_cost:
            upper_price_bound = min(upper_price_bound, self.agent.config.needs_satisfaction_cost)
            lower_price_bound = min(lower_price_bound, self.agent.config.needs_satisfaction_cost)

        if self.agent.get_time_to_satisfy() and self.agent.get_time_to_satisfy() < self.agent.get_timeout():
            lower_price_bound = upper_price_bound

        price = self.random(lower_price_bound, upper_price_bound)

        upper_resource_bound = min(upper_resource_bound, (
                self.agent.money_total - self.agent.money_in_use
                + (own_offer.money if own_offer else 0)
        ) / price)

        upper_resource_bound = round(upper_resource_bound, self.ACCURACY)

        if upper_resource_bound == 0:
            return Offer(OfferType.BREAKDOWN_OFFER, False, 0, 0)
        return Offer(
            OfferType.COUNTER_OFFER,
            False,
            resource=upper_resource_bound,
            money=round(upper_resource_bound * price, self.ACCURACY)
        )

    def sell_counter_offer(self, own_offer, other_offers):
        """
        :param own_offer: offer, may be None if no previous own offer
        :param other_offers: a dict of offers to counter
        :return: a counter or breakdown offer
        """
        prev_offers = [oo for o in other_offers.values() for oo in o.other_offers]
        other_offers = [o for o in other_offers.values() if o.resource]

        upper_resource_bound = min(
            sum(o.resource for o in other_offers),
            self.agent.resource_total - self.agent.resource_in_use + (own_offer.resource if own_offer else 0)
        )
        upper_resource_bound = round(upper_resource_bound, self.ACCURACY)

        if upper_resource_bound == 0:
            return Offer(OfferType.BREAKDOWN_OFFER, True, 0, 0)

        lower_price_bound = max(o.money / o.resource for o in other_offers)
        upper_price_bound = min(o.money / o.resource for o in prev_offers) if prev_offers else self.MAX_PRICE
        if own_offer:
            upper_price_bound = min(
                upper_price_bound,
                max((own_offer.money / own_offer.resource) * (1 - self.minimal_price_change), lower_price_bound)
            )

        if self.agent.config.production_cost:
            lower_price_bound = self.agent.config.production_cost

        if upper_price_bound < lower_price_bound:
            return Offer(OfferType.BREAKDOWN_OFFER, True, 0, 0)

        price = self.random(lower_price_bound, upper_price_bound)
        resource = upper_resource_bound

        return Offer(
            OfferType.COUNTER_OFFER,
            is_sell_offer=True,
            money=round(price * resource, self.ACCURACY),
            resource=resource)

    #################################
    # below are some helper methods #
    #################################

    def resource_increase_limit(self):
        limit = self.agent.config.storage_limit - self.agent.resource_total + self.agent.current_needs

        return limit

    def random(self, a, b):
        return round(random.uniform(a, b), self.ACCURACY)
