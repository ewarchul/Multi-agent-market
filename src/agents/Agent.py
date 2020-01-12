from agents.AgentBase import AgentBase

import logger

import datetime
import threading
import asyncio
import spade


class Agent(AgentBase):
    LOGIC_TIME_QUANT = 10 * AgentBase.TIME_QUANT
    TIMEOUT = LOGIC_TIME_QUANT

    class CreateOffers(spade.behaviour.CyclicBehaviour):
        """
        Beaviour for checking if an offer is to be created
        """
        def __init__(self):
            super(Agent.CreateOffers, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.LOGIC_TIME_QUANT)

            with logger.ExceptionCatcher('CreateOffers'):
                self.agent.run_transaction_in_server_mode(selling=False)
                self.agent.run_transaction_in_server_mode(selling=True)

    class GenerateProduct(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for producing storage product. 
        """
        def __init__(self):
            self.last_generate_time = datetime.datetime.now()
            super(Agent.GenerateProduct, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.LOGIC_TIME_QUANT)

            with logger.ExceptionCatcher('GenerateProduct'):
                current_time = datetime.datetime.now()

                dt = self.last_generate_time - current_time
                self.agent.produce(current_time, dt)
                self.last_generate_time = current_time

    class DropProduct(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for droping storage product.
        """
        def __init__(self):
            super(Agent.DropProduct, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.LOGIC_TIME_QUANT)

            with logger.ExceptionCatcher('DropProduct'):
                self.agent.drop()

    class ManageNeeds(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for needs generation.
        """
        def __init__(self):
            super(Agent.ManageNeeds, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.LOGIC_TIME_QUANT)

            with logger.ExceptionCatcher('ManageNeeds'):
                current_time = datetime.datetime.now()
                to_satisfy = datetime.timedelta(seconds=self.agent.config.needs_satisfaction_timeout)

                self.agent.create_needs(current_time, to_satisfy)

                await asyncio.sleep(to_satisfy.total_seconds())

                self.agent.check_satisfaction()

    class GenerateIncome(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for income generate. 
        """
        def __init__(self):
            super(Agent.GenerateIncome, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.config.income_time)

            with logger.ExceptionCatcher('GenerateIncome'):
                current_time = datetime.datetime.now()
                dt = datetime.timedelta(seconds=self.agent.config.income_time)

                self.agent.income(current_time, dt)

    async def setup(self):
        await super(Agent, self).setup()

        self.generate_product_behaviour = self.GenerateProduct()
        self.add_behaviour(self.generate_product_behaviour)

        self.generate_income_behaviour = self.GenerateIncome()
        self.add_behaviour(self.generate_income_behaviour)

        self.manage_needs_behaviour = self.ManageNeeds()
        self.add_behaviour(self.manage_needs_behaviour)

        self.create_offers_behaviour = self.CreateOffers()
        self.add_behaviour(self.create_offers_behaviour)

    def __init__(self, agent_id, connections, config):

        self.generate_product_behaviour = None
        self.generate_income_behaviour = None
        self.manage_needs_behaviour = None
        self.drop_product_behaviour = None
        self.create_offers_behaviour = None

        super(Agent, self).__init__(agent_id, connections, config)

        self.money_total = 0
        self.money_in_use = 0

        self.resource_total = 0
        self.resource_in_use = 0

        self.current_needs = 0

        self.state_lock = threading.Lock()

        self.modify_state(self.config.initial_resource, self.config.initial_money, 'Initial state')

    def pretty_print_me(self):
        """
        Prints agent params.
        """
        print(f"\n AGENT_ID: {self.id} \n \
                TOTAL RESOURCE = {self.resource_total} \n \
                RESOURCE IN USE =  {self.resource_in_use} \n \
                STORAGE LIMIT =  {self.config.storage_limit} \n \
                TOTAL MONEY = {self.money_total} $ \n \
                MONEY IN USE {self.money_in_use} $ \n")

    def get_initial_buy_offer(self):
        """
        Prepares initial buy offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = False
        """
        with self.state_lock:
            offer = self.policy.initial_buy_offer()
            if offer:
                self.money_in_use += offer.money

            return offer

    def get_initial_sell_offer(self):
        """
        Prepares initial sell offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = True
        """
        with self.state_lock:
            offer = self.policy.initial_buy_offer()
            if offer:
                self.resource_in_use += offer.resource

            return offer

    def get_counter_offer(self, offer, sender_offers):
        """
        Prepare counter offer.

        Counter offer should not have other_offers field set, as it is done
        in negotiate_server only

        :param offer: previous own offer, None if countering initial offer
        :param sender_offers: dict mapping agents to their offers
        :return: Offer object
        """

        with self.state_lock:
            offer = self.policy.sell_counter_offer(offer, sender_offers)\
                if offer.is_sell_offer else self.policy.buy_counter_offer(offer, sender_offers)

            if offer.is_sell_offer:
                self.resource_in_use += offer.resource - offer.resource
            else:
                self.money_in_use += offer.money - offer.money

            return offer

    def get_timeout(self):
        """
        Generates timeout
        """
        return self.TIMEOUT

    def check_accepted(self, offer, sender_offers):
        """
        Checks if a subset of sender_offers is to be accepted
        :param sender_offers: dict mapping agents to their offers
        :return: a pair of dicts mapping agents to their offer for offers to be accepted
        """
        possibly_accepted = {
            s: o
            for s, o in sender_offers.items()
            if offer.money / offer.resource == o.money / o.resource and o.resource <= offer.resource
        }

        if not possibly_accepted:
            return None

        accepted = {}
        resource_left = offer.resource

        for sender, o in possibly_accepted.items():
            if resource_left >= o.resource:
                resource_left -= o.resource
                accepted[sender] = o

        return accepted

    def accepted_offers(self, offer, sender_offers):
        """
        Save negotiation result

        :param offer: Own offer
        :param sender_offers: Offers accepted and confirmed for this offer
        :return: None
        """

        with self.state_lock:
            if offer.is_sell_offer:
                self.resource_in_use -= offer.resource
            else:
                self.money_in_use -= offer.money

            money_change = sum(o.money for o in sender_offers)
            resource_change = sum(o.resource for o in sender_offers)

            if offer.is_sell_offer:
                resource_change = -resource_change
            else:
                money_change = -money_change

            self.modify_state(resource_change, money_change, 'Offers accepted')

    def modify_state(self, resource_change, money_change, reason):
        old_resource = self.resource_total
        old_money = self.money_total

        if self.current_needs > 0 and resource_change > 0:
            if resource_change > self.current_needs:
                resource_change -= self.current_needs
                self.current_needs = 0
            else:
                self.current_needs -= resource_change
                resource_change = 0

        self.resource_total += resource_change
        if self.resource_total > self.config.storage_limit:
            money_change -= (self.config.storage_limit - self.resource_total) * self.config.utilization_cost

        self.money_total += money_change
        if self.money_total < 0:
            self.bankrupt()

        logger.logger.log(
            logger.EVENT_AGENT_STATE_CHANGED,
            id=self.id,
            reason=reason,
            old_resource=old_resource,
            resource=self.resource_total,
            old_money=old_money,
            money=self.money_total
        )

    def create_needs(self, time, dt):
        with self.state_lock:
            needs = self.config.needs(time, dt)

            free_resource = self.resource_total - self.resource_in_use
            if free_resource > 0:
                if free_resource > needs:
                    self.modify_state(-needs, 0, 'Needs created')
                    self.resource_total -= needs
                    needs = 0
                else:
                    needs -= free_resource
                    self.modify_state(-free_resource, 0, 'Needs created')

            self.current_needs += needs

    def produce(self, time, dt):
        with self.state_lock:
            limit = self.config.production_limit(time, dt)
            resource_change = self.policy.produce(limit)
            if resource_change:
                cost = resource_change * self.config.production_cost
                self.modify_state(resource_change, -cost, 'Production')

    def income(self, time, dt):
        with self.state_lock:
            income = self.config.income(time, dt)
            if income:
                self.modify_state(0, income, 'Income')

    def drop_product(self):
        with self.state_lock:
            drop = self.policy.drop_storage()
            cost = -drop * self.config.utilization_cost
            if drop:
                self.modify_state(-drop, cost, 'Dropped product')

    def check_satisfaction(self):
        with self.state_lock:
            if self.current_needs > 0:
                penalty = self.current_needs * self.config.needs_satisfaction_penalty

                self.modify_state(0, -penalty, 'Needs satisfaction penalty')

    def bankrupt(self):
        self.pause()
        self.remove_behaviour(self.generate_product_behaviour)
        self.remove_behaviour(self.generate_income_behaviour)
        self.remove_behaviour(self.manage_needs_behaviour)
        self.remove_behaviour(self.create_offers_behaviour)

        logger.logger.log(
            logger.EVENT_AGENT_BANKRUPTED,
            self.id
        )
