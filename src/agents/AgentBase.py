import threading
import asyncio

import spade

import logger
from agents.Session import Session
from agents.Message import deserialize_message
from agents.Offer import Offer, OfferType, make_accepting, make_confirmation


class AgentBase(spade.agent.Agent):
    """
    Implementation of Multi-agent system part of agent
    """
    HOST = 'localhost'
    TIME_QUANT = 0.05
    CLIENT_TIMEOUT_FACTOR = 2

    def get_agent_jid(self, agent_id):
        """
        :param agent_id:
        :return: JID for given ID
        """
        return f'agent_{agent_id}@{self.HOST}'

    def get_agent_id(self, agent_jid):
        """
        :param agent_jid:
        :return: ID for given JID
        """
        return agent_jid[len('agent_'):-(len(self.HOST) + 1)]

    class SendMessages(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for sending messages
        """
        def __init__(self):
            super(AgentBase.SendMessages, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.TIME_QUANT)

            with logger.ExceptionCatcher('SendMessages'):
                sessions = self.agent.get_sessions()
                for sess in sessions:
                    messages = list(sess.take_all_out_messages())
                    for msg in messages:
                        try:
                            await self.send(msg.serialize())

                            logger.logger.log(
                                logger.EVENT_MESSAGE_SENT,
                                sender=self.agent.jid,
                                receiver=msg.agent,
                                content=msg.body
                            )
                        except Exception as e:
                            logger.logger.log(
                                logger.EVENT_EXCEPTION,
                                where=f'Agent {self.agent.id} SendMessages',
                                type=str(type(e)),
                                exception=str(e)
                            )

                    if sess.ended:
                        self.agent.remove_session(sess.session_id)

    class ReceiveMessage(spade.behaviour.CyclicBehaviour):
        """
        Behaviour for receiving messages
        """
        def __init__(self):
            super(AgentBase.ReceiveMessage, self).__init__()

        async def run(self):
            with logger.ExceptionCatcher('ReceiveMessage'):
                spade_msg = await self.receive(self.agent.TIME_QUANT)

                if not spade_msg:
                    return

                msg = deserialize_message(spade_msg)

                logger.logger.log(
                    logger.EVENT_MESSAGE_RECEIVED,
                    sender=msg.agent,
                    receiver=self.agent.jid,
                    content=msg.body
                )

                if msg.receiver_session is not None and msg.receiver_session in self.agent.sessions:
                    self.agent.sessions[msg.receiver_session].add_in_message(msg)
                elif msg.receiver_session is not None:
                    logger.logger.log(
                        logger.EVENT_EXCEPTION,
                        where=f'Agent {self.agent.id} ReceiveMessage',
                        type='Invalid session',
                        exception=f'{msg.receiver_session}'
                    )
                else:
                    self.agent.received_msg_without_session(msg)

    def __init__(self, agent_id, connections, config):
        """
        Creates agent

        :param agent_id: ID of the agent
        :param connections: a collections of ids of agents that this agent is connected to
        :param config: agent configuration
        """
        self.id = str(agent_id)
        self.connections = list(map(str, connections))
        self.config = config
        self.policy = config.build_policy(self)

        self.jid = self.get_agent_jid(agent_id)

        self.session_lock = threading.Lock()
        self.sessions = {}
        self.next_session_id = 0

        self.sender_behaviour = None
        self.receiver_behaviour = None

        self.running = False

        super(AgentBase, self).__init__(self.jid, self.jid)

    async def setup(self):
        """ spade setup """
        self.sender_behaviour = self.SendMessages()
        self.receiver_behaviour = self.ReceiveMessage()

        self.add_behaviour(self.sender_behaviour)
        self.add_behaviour(self.receiver_behaviour)

        self.running = True

        logger.logger.log(
            logger.EVENT_AGENT_STARTED,
            name=self.id,
            connection=', '.join(map(str, self.connections)),
            jid=self.jid,
            policy=self.config.get_policy_name()
        )

    def pause(self):
        if self.running:
            self.remove_behaviour(self.sender_behaviour)
            self.remove_behaviour(self.receiver_behaviour)

            logger.logger.log(
                logger.EVENT_AGENT_KILLED,
                id=self.id
            )

        self.running = False

    def restore(self):
        if not self.running:
            self.sender_behaviour = self.SendMessages()
            self.receiver_behaviour = self.ReceiveMessage()
            self.add_behaviour(self.sender_behaviour)
            self.add_behaviour(self.receiver_behaviour)

            logger.logger.log(
                logger.EVENT_AGENT_RESTARTED,
                id=self.id
            )

        self.running = True

    def create_session(self):
        """
        Creates a session with locally-unique id
        :return: created session
        """
        with self.session_lock:
            sess = Session(self, self.next_session_id)
            self.next_session_id += 1
            self.sessions[sess.session_id] = sess
            return sess

    def remove_session(self, session_id):
        """
        Removes session
        :param session_id: ID of session that is to be removed
        :return: None
        """
        with self.session_lock:
            self.sessions.pop(session_id)

    def get_sessions(self):
        """
        :return: a list of all open sessions
        """
        with self.session_lock:
            return list(self.sessions.values())

    def received_msg_without_session(self, msg):
        """
        Manage message received without session

        if is INITIAL_OFFER, starts new negotiation

        :param msg: message
        :return: None
        """
        agent = self.get_agent_id(msg.agent)
        offer = msg.body
        agent_sess_id = msg.sender_session

        if not hasattr(offer, 'type'):
            logger.logger.log(
                logger.EVENT_EXCEPTION,
                where='received_msg_without_session',
                type='Invalid offer object',
                exc=str(offer)
            )
        elif not offer.type == OfferType.INITIAL_OFFER:
            logger.logger.log(
                logger.EVENT_EXCEPTION,
                where='received_msg_without_session',
                type='Received offer is not initial',
                exc=offer.type
            )
        else:
            t = threading.Thread(target=self.run_transaction_in_client_mode, args=(agent, offer, agent_sess_id))
            t.daemon = True
            t.start()

    def run_transaction_in_client_mode(self, agent, initial_offer, agent_session_id):
        """
        Runs transaction in client mode
        :param agent: negotiation partner
        :param initial_offer: partner's offer
        :param agent_session_id: id of partner's session
        :return: None
        """
        session = self.create_session()
        self.negotiate_client(session, initial_offer, agent, agent_session_id)
        session.end()

    def run_transaction_in_server_mode(self, selling):
        """
        Runs in server mode (as '1' in '1 to n')

        :param selling: True if try to sell, else False
        :return: None
        """
        session = self.create_session()

        offer = self.get_initial_sell_offer() if selling else self.get_initial_buy_offer()
        if offer:
            def run():
                partners = self.get_negotiation_partners(selling)

                self.negotiate_server(session, offer, partners)

                session.end()

            t = threading.Thread(target=run)
            # t.daemon = True
            t.start()

    def negotiate_server(self, session, initial_offer, partners):
        """
        Negotiate as a server

        :param session: session
        :param initial_offer: initial offer to send to partners
        :param partners: initial set of partners
        :return: None
        """
        timeout = self.get_timeout()

        offer = initial_offer
        partners_sessions = {p: None for p in partners}

        confirmation_offers = {}

        while len(partners) > 0:
            session.send_multiple(offer, partners_sessions)

            if not offer:
                break

            senders, offers, sessions = session.receive(senders=partners, timeout=timeout)
            if not offer or not offers:
                break

            # remove breakdown offers
            aos = list(zip(*[(a, o, s) for a, o, s in zip(senders, offers, sessions) if o]))

            if not aos:
                break

            senders, offers, sessions = aos

            partners.intersection_update(senders)
            partners_sessions = {a: sess for a, sess in zip(senders, sessions)}
            sender_offers = {s: o for s, o in zip(senders, offers) if s in partners}

            accept_offers = self.check_accepted(offer, sender_offers)

            if accept_offers:
                confirmation_offers = self.finalize_negotiations(
                    accept_offers, {s: o for s, o in sender_offers.items() if s not in accept_offers},
                    session, partners_sessions, timeout)
                break

            offer = self.get_counter_offer(offer, sender_offers)
            self.set_previous_offers(offer, sender_offers)

        self.accepted_offers(offer, confirmation_offers)

        if not offer:
            logger.logger.log(
                logger.EVENT_SERVER_NEGOTIATION_BREAKDOWN,
                id=self.id
            )
        elif not partners:
            logger.logger.log(
                logger.EVENT_ALL_CLIENTS_NEGOTIATION_BREAKDOWN,
                id=self.id
            )

    def set_previous_offers(self, offer, previous_dict):
        offer.other_offers = list(previous_dict.values())
        for o in offer.other_offers:
            o.other_offers = None

    def finalize_negotiations(self, accept_offers, reject_offers, session, partner_sessions, timeout):
        """
        Finalizes negotiation as a server - accept selected offers, reject other

        :param accept_offers: dict mapping agents to offers that are to be accepted
        :param reject_offers: dict mapping agents to offers that are to be rejected
        :param session: session
        :param partner_sessions: dict mapping agents to their session IDs
        :param timeout: timeout for receiving messages
        :return: dict mapping agents to confirmation offers
        """
        for sender, offer in accept_offers.items():
            own = make_accepting(offer, list(accept_offers.values()))
            session.send(own, sender, partner_sessions[sender])
        for sender, _ in reject_offers.items():
            own = Offer(OfferType.BREAKDOWN_OFFER, 0, 0, list(accept_offers.values()))
            session.send(own, sender, partner_sessions[sender])

        senders, offers, sessions = session.receive(partner_sessions, timeout)

        return {s: o for s, o in zip(senders, offers) if o}

    def negotiate_client(self, session, initial_offer, partner, partner_session):
        """
        Negotiate as client

        :param session: session
        :param initial_offer: received offer
        :param partner: partner agent
        :param partner_session: partner's session ID
        :return: None
        """
        partner_offer = initial_offer
        own_offer = self.get_counter_offer(None, {partner: partner_offer})

        timeout = self.get_timeout() * self.CLIENT_TIMEOUT_FACTOR

        while partner_offer.type in (OfferType.INITIAL_OFFER, OfferType.COUNTER_OFFER):
            session.send(own_offer, partner, partner_session)

            partner_offer = None

            if not own_offer:
                logger.logger.log(
                    logger.EVENT_CLIENT_NEGOTIATION_BREAKDOWN,
                    id=self.id,
                    server_id=partner
                )
                break

            _, pos, _ = session.receive(senders={partner}, timeout=timeout)

            if not pos:
                logger.logger.log(
                    logger.EVENT_SERVER_FAILED_TO_RESPOND,
                    id=self.id,
                    server_id=partner
                )
                break

            partner_offer = pos[0]

            if partner_offer.type == OfferType.ACCEPTING_OFFER:
                own_offer = make_confirmation(partner_offer)
                session.send(own_offer, partner, partner_session)

            if not partner_offer:
                break

            own_offer = self.get_counter_offer(own_offer, {partner: partner_offer})
            self.set_previous_offers(own_offer, {partner: partner_offer})

        self.accepted_offers(own_offer, {partner: partner_offer} if partner_offer else {})

    def get_negotiation_partners(self, selling):
        """
        Returns initial negotiation partners list

        :param selling: if negotiation's purpose is to sell resource
        :return: a set of agents' IDs
        """
        return set(self.connections)

    def get_initial_buy_offer(self):
        """
        Prepares initial buy offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = False
        """
        raise NotImplementedError

    def get_initial_sell_offer(self):
        """
        Prepares initial sell offer

        :return: Offer object with type = INITIAL_OFFER and is_sell_offer = True
        """
        raise NotImplementedError

    def get_timeout(self):
        """

        :return: time to wait for responses
        """
        raise NotImplementedError

    def get_counter_offer(self, offer, sender_offers):
        """
        Prepare counter offer.

        Counter offer should not have other_offers field set, as it is done
        in negotiate_server only

        :param offer: previous own offer, None if countering initial offer
        :param sender_offers: dict mapping agents to their offers
        :return: Offer object
        """
        raise NotImplementedError

    def check_accepted(self, offer, sender_offers):
        """
        Checks if a subset of sender_offers is to be accepted

        :param offer: previous own offer
        :param sender_offers: dict mapping agents to their offers
        :return: a pair of dicts mapping agents to their offer for offers to be accepted
        """
        raise NotImplementedError

    def accepted_offers(self, offer, sender_offers):
        """
        Save negotiation result

        :param offer: Own offer
        :param sender_offers: Offers accepted and confirmed for this offer
        :return: None
        """
        raise NotImplementedError
