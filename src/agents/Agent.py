from agents.AgentBase import AgentBase
from config import AgentConfig
from agents.Offer import Offer, OfferType

import threading
import spade


class Agent(AgentBase):
    class Produce(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for producing storage product. 
        """
        pass
    class DropStorage(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for droping storage product.
        """
        
    def __init__(self, agent_id, connections, config):
        super(Agent, self).__init__(agent_id, connections, config)
    def get_initial_buy_offer(self, resource_amount=1, price=1):
        """
        Prepares initial buy offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = False
        """
        money_lock = threading.Lock()  
        with money_lock:
            if self.config.money_in_use >= price:

                self.config.money_in_use -= price

                buy_offer = Offer(
                    offer_type = Offer.INITIAL_OFFER,
                    resource = resource_amount,
                    money = price,
                    is_sell_offer = False
                )
            else:
                return None  
        return buy_offer
    def get_initial_sell_offer(self, resource_amount=1, price=1):
        """
        Prepares initial sell offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = True
        """
        resource_lock = threading.Lock()  
        with resource_lock:
            if self.config.resource_in_use >= resource_amount:

                self.config.resource_in_use -= resource_amount 

                sell_offer = Offer(
                    offer_type = Offer.INITIAL_OFFER,
                    resource = resource_amount,
                    money = price,
                    is_sell_offer = True
                )
            else:
                return None  
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
        new_price = 0.9*offer.money  
        new_resource_amount = 1.1*offer.resource
        with resource_lock:
            self.config.resource_in_use -= 0.1*new_resource_amount
        return Offer(
                    offer_type = Offer.COUNTER_OFFER,
                    resource = offer.resource,
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
        rejected_offers = {s: o for s, o in sender_offers.items() if o.type != OfferType.ACCEPTING_OFFER}

        for offer in rejected_offers.items():
            self.config.resource_in_use += offer.resource

        return {s: o for s, o in sender_offers.items() if o.type == OfferType.ACCEPTING_OFFER}
    def accepted_offers(self, offer, sender_offers):
        """
        Save negotiation result

        :param offer: Own offer
        :param sender_offers: Offers accepted and confirmed for this offer
        :return: None
        """
        resource_sold  = sum([offer.resource for agent, offer in sender_offers.items()])
        money_earnt  = sum([offer.money for agent, offer in sender_offers.items()])
        resource_lock = threading.Lock()  
        with resource_lock:
            self.config.initial_resource -= resource_sold
            self.config.initial_money += money_earnt
            self.config.money_in_use += money_earnt

