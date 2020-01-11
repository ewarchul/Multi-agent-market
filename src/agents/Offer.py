import enum


class OfferType(enum.Enum):
    """
    Offer types
    """
    INITIAL_OFFER = 'Initial'
    COUNTER_OFFER = 'Counter'
    ACCEPTING_OFFER = 'Accepting'
    BREAKDOWN_OFFER = 'Breakdown'
    CONFIRMATION_OFFER = 'Confirmation'


class Offer:
    """
    Offer object.

    If used as boolean, returns False iff it is a breakdown offer
    """
    def __init__(self, offer_type, is_sell_offer, resource, money, other_offers=()):
        """
        Creates offer.

        :param offer_type: Type of the offer
        :param is_sell_offer: True if selling resource, False if buying
        :param resource: Amount of resource
        :param money: Amount of unit
        :param other_offers:
        """
        self.type = offer_type
        self.resource = resource
        self.money = money
        self.other_offers = other_offers
        self.is_sell_offer = is_sell_offer

    def __eq__(self, other):
        if not hasattr(other, 'resource') or not hasattr(other, 'money'):
            return False

        return self.resource == other.resource and self.money == other.money

    def __str__(self):
        return f'{self.type} {"sell" if self.is_sell_offer else "buy"} offer for ' \
               f'{self.resource} resource for {self.money} money with ' \
               f'info about {len(self.other_offers)} other offers' \
                if self else 'Breakdown offer'

    def __bool__(self):
        return self.type != OfferType.BREAKDOWN_OFFER


def make_accepting(offer, other_offers):
    """
    Creates offer that given offer
    :param offer: the accepted offer
    :param other_offers: all offers that were accepted
    :return: Accepting offer
    """
    return Offer(
        OfferType.ACCEPTING_OFFER,
        not offer.is_sell_offer,
        offer.resource,
        offer.money,
        other_offers
    )


def make_confirmation(offer):
    """
    Creates confirmation for given offer
    :param offer: the offer
    :return: Confirmation offer
    """
    return Offer(
        OfferType.CONFIRMATION_OFFER,
        not offer.is_sell_offer,
        offer.resource,
        offer.money
    )
