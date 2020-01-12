from agents.AgentBase import AgentBase
from config import AgentConfig
from agents.Offer import Offer, OfferType

import logger

import datetime
import threading
import random
import asyncio
import spade

class Agent(AgentBase):
    class GenerateProduct(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for producing storage product. 
        """
        def __init__(self):
            super(Agent.GenerateProduct, self).__init__()
        async def run(self):
            await asyncio.sleep(self.agent.TIME_QUANT)
            current_time = datetime.datetime.now() 
            dt = datetime.datetime.now() + datetime.timedelta(seconds=self.agent.TIME_QUANT) 
            resource_at_start = self.agent.config.initial_resource 
            money_at_start = self.agent.config.initial_money 
            if self.agent.config.initial_resource < self.agent.config.storage_limit and random.random() > 0.8:
                production_limit = self.agent.config.production_limit(current_time, dt)
                generated_product = random.uniform(0, production_limit)
                self.agent.config.initial_money -= generated_product*self.agent.config.production_cost 
                self.agent.config.initial_resource += generated_product 
                self.agent.config.resource_in_use = self.agent.config.initial_resource
                self.agent.config.money_in_use = self.agent.config.initial_money
                logger.logger.log(
                        logger.EVENT_AGENT_STATE_CHANGED,
                            id=self.agent.jid,
                            reason='Extra product generation',
                            old_resource = resource_at_start,
                            resource=self.agent.config.initial_resource,
                            old_money=money_at_start,
                            money=self.agent.config.initial_money
                        )
    class DropProduct(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for droping storage product.
        """
        def __init__(self):
            super(Agent.DropProduct, self).__init__()
        async def run(self):
            await asyncio.sleep(self.agent.TIME_QUANT)
            resource_at_start = self.agent.config.initial_resource 
            money_at_start = self.agent.config.initial_money 
            if self.agent.config.initial_resource > self.agent.config.storage_limit:
                self.agent.config.initial_resource = self.agent.config.storage_limit 
                self.agent.config.initial_money -= self.agent.config.utilization_cost
                self.agent.config.money_in_use = self.agent.config.initial_money
                logger.logger.log(
                        logger.EVENT_AGENT_STATE_CHANGED,
                            id=self.agent.jid,
                            reason='Extra product storage penalty',
                            old_resource = resource_at_start,
                            resource=self.agent.config.initial_resource,
                            old_money=money_at_start,
                            money=self.agent.config.initial_money
                        )
    class GenerateNeeds(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for needs generation.
        """
        def __init__(self):
            super(Agent.GenerateNeeds, self).__init__()
        async def run(self):
            await asyncio.sleep(self.agent.TIME_QUANT)
            current_time = datetime.datetime.now() 
            dt = datetime.datetime.now() + datetime.timedelta(seconds=self.agent.TIME_QUANT) 
            if self.agent.config.current_needs == self.agent.config.initial_resource:
                self.agent.config.current_needs = self.agent.config.needs(current_time, dt) 
    class NeedsPenalty(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for needs statisfaction penalty. 
        """
        def __init__(self):
            super(Agent.NeedsPenalty, self).__init__()
        async def run(self):
            await asyncio.sleep(5)#self.agent.config.needs_satisfaction_timeout)
            money_at_start = self.agent.config.initial_money 
            self.agent.config.initial_money -= self.agent.config.needs_satisfaction_cost 
            self.agent.config.money_in_use = self.agent.config.initial_money
            logger.logger.log(
                        logger.EVENT_AGENT_STATE_CHANGED,
                            id=self.agent.jid,
                            reason='Needs statisfaction penalty',
                            old_resource = self.agent.config.initial_resource,
                            resource=self.agent.config.initial_resource,
                            old_money=money_at_start,
                            money=self.agent.config.initial_money
                        )
    class GenerateIncome(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for income generate. 
        """
        def __init__(self):
            super(Agent.GenerateIncome, self).__init__()
        async def run(self):
            await asyncio.sleep(5)#self.agent.config.income_time)
            current_time = datetime.datetime.now() 
            dt = datetime.datetime.now() + datetime.timedelta(seconds=self.agent.TIME_QUANT) 
            money_at_start = self.agent.config.initial_money 
            self.agent.config.initial_money += self.agent.config.income(current_time, dt) 
            self.agent.config.money_in_use += self.agent.config.initial_money 
            logger.logger.log(
                        logger.EVENT_AGENT_STATE_CHANGED,
                        id=self.agent.jid,
                        reason='Money income',
                        old_resource = self.agent.config.initial_resource,
                        resource=self.agent.config.initial_resource,
                        old_money=money_at_start,
                        money=self.agent.config.initial_money
                        )
    async def setup(self):

        await super(Agent, self).setup()

        self.generate_product_behaviour = self.GenerateProduct()
        self.add_behaviour(self.generate_product_behaviour)

        self.generate_income_behaviour = self.GenerateIncome()
        self.add_behaviour(self.generate_income_behaviour)

        self.generate_needs_behaviour = self.GenerateNeeds()
        self.add_behaviour(self.generate_needs_behaviour)

        self.drop_product_behaviour = self.DropProduct()
        self.add_behaviour(self.drop_product_behaviour)

        self.needs_penalty_behaviour = self.NeedsPenalty()
        self.add_behaviour(self.needs_penalty_behaviour)

    def __init__(self, agent_id, connections, config):

        self.generate_product_behaviour = None
        self.generate_income_behaviour = None
        self.generate_needs_behaviour = None 
        self.drop_product_behaviour = None 
        self.needs_penalty_behaviour = None 

        super(Agent, self).__init__(agent_id, connections, config)

    def pretty_print_me(self):
        """
        Prints agent params.
        """
        print(f"\n AGENT_ID: {self.jid} \n \
                TOTAL RESOURCE = {self.config.initial_resource} \n \
                RESOURCE IN USE =  {self.config.resource_in_use} \n \
                STORAGE LIMIT =  {self.config.storage_limit} \n \
                TOTAL MONEY = {self.config.initial_money} $ \n \
                MONEY IN USE {self.config.money_in_use} $ \n")
    def get_initial_buy_offer(self, resource_amount=100, price=100):
        """
        Prepares initial buy offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = False
        """
        print("----------------- BEFOER INITIAL BUY OFFER ------------\n")
        self.pretty_print_me()
        money_lock = threading.Lock()  
        with money_lock:
            if self.config.resource_in_use >= resource_amount:

                self.config.resource_in_use -= resource_amount

                buy_offer = Offer(
                    offer_type = OfferType.INITIAL_OFFER,
                    resource = resource_amount,
                    money = price,
                    is_sell_offer = False
                )
            else:
                return None  
        print("----------------- AFTER INITIAL BUY OFFER ------------\n")
        self.pretty_print_me()
        return buy_offer
    def get_initial_sell_offer(self, resource_amount=100, price=100):
        """
        Prepares initial sell offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = True
        """
        print("----------------- BEFORE INITIAL SELL OFFER ------------\n")
        self.pretty_print_me()
        resource_lock = threading.Lock()  
        with resource_lock:
            if self.config.resource_in_use >= resource_amount:

                self.config.resource_in_use -= resource_amount 

                sell_offer = Offer(
                    offer_type = OfferType.INITIAL_OFFER,
                    resource = resource_amount,
                    money = price,
                    is_sell_offer = True
                )
            else:
                return None  
        print("----------------- AFTER INITIAL SELL OFFER ------------\n")
        self.pretty_print_me()
        return sell_offer
    def get_counter_offer(self, offer, sender_offers):
        """
        Prepare counter offer.

        Counter offer should not have other_offers field set, as it is done
        in negotiate_server only

        :param offer: previous own offer, None if countering initial offer
        :param sender_offers: dict mapping agents to their offers
        :return: Offer object
        """
        print("----------------- BEFORE COUNTER OFFER ------------\n")
        self.pretty_print_me()
        if offer is None:
            new_price = 0.9*min([o.money for a, o in sender_offers.items()])
            new_resource_amount = 1.1*min([o.resource for a, o in sender_offers.items()])
        else:
            new_price = 0.9*offer.money  
            new_resource_amount = 1.1*offer.resource
        print("----------------- AFTER COUNTER OFFER ------------\n")
        self.pretty_print_me()
        return Offer(
                    offer_type = OfferType.COUNTER_OFFER,
                    resource = new_resource_amount, 
                    money = new_price,
                    is_sell_offer = True
                )
    def get_timeout(self):
        """
        Generates timeout which depends on agent internal config.
        """
        return self.config.needs_satisfaction_timeout 
    def check_accepted(self, sender_offers):
        """
        Checks if a subset of sender_offers is to be accepted
        :param sender_offers: dict mapping agents to their offers
        :return: a pair of dicts mapping agents to their offer for offers to be accepted
        """
        offers_sorted = dict(sorted(sender_offers.items(), key=lambda x: (x[1].money, -x[1].resource)))

        accepted_offers = []
        for offer in offers_sorted.items():
            if self.config.money_in_use - offer[1].money and random.random() > 0.8:
                accepted_offers.append(offer) 
        return dict(accepted_offers) 
    def accepted_offers(self, offer, sender_offers, agent_role):
        """
        Save negotiation result

        :param offer: Own offer
        :param sender_offers: Offers accepted and confirmed for this offer
        :return: None
        """
        resource_sold  = sum([offer.resource for agent, offer in sender_offers.items()])
        money_earnt  = sum([offer.money for agent, offer in sender_offers.items()])
        print("=========== DURING TRANSACTION ===========\n")
        self.pretty_print_me()
        resource_lock = threading.Lock()  
        with resource_lock:
            if agent_role is "SERVER" and offer.type is OfferType.CONFIRMATION_OFFER:
                self.config.initial_resource -= resource_sold
                self.config.resource_in_use = self.config.initial_resource
                self.config.initial_money += money_earnt
                self.config.money_in_use += money_earnt
            elif agent_role is "CLIENT" and offer.type is OfferType.CONFIRMATION_OFFER:
                self.config.initial_resource += offer.resource
                self.config.resource_in_use = self.config.initial_resource
                self.config.initial_money -= offer.money 
                self.config.money_in_use -= offer.money
        print("=========== AFTER FINALIZED TRANSACTION ===========\n")
        self.pretty_print_me()
        

