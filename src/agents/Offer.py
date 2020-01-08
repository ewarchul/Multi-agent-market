import enum


class OfferType(enum.Enum):
    INITAL_OFFER = 'Initial'
    COUNTER_OFFER = 'Counter'
    ACCEPTING_OFFER = 'Accepting'
    BREAKDOWN_OFFER = 'Breakdown'
    CONFIRMATION_OFFER = 'Confirmation'


class Offer:
    def __init__(self, offer_type, is_sell_offer, resource, money, other_offers=()):
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
    return Offer(
        OfferType.ACCEPTING_OFFER,
        not offer.is_sell_offer,
        offer.resource,
        offer.money,
        other_offers
    )


def make_confirmation(offer):
    return Offer(
        OfferType.CONFIRMATION_OFFER,
        not offer.is_sell_offer,
        offer.resource,
        offer.money
    )
