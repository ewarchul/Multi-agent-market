import threading
import asyncio

import spade

import logger
from agents.Session import Session
from agents.Message import deserialize_message


class AgentBase(spade.agent.Agent):
    HOST = 'localhost'
    TIME_QUANT = 0.1

    def get_agent_jid(self, agent_id):
        return f'agent_{agent_id}@{self.HOST}'

    def get_agent_id(self, agent_jid):
        return agent_jid[len('agent_'):-(len(self.HOST) + 1)]

    class SendMessages(spade.behaviour.CyclicBehaviour):
        def __init__(self):
            super(AgentBase.SendMessages, self).__init__()

        async def run(self):
            await asyncio.sleep(self.agent.TIME_QUANT)

            sessions = self.agent.get_sessions()
            for sess in sessions:
                for msg in sess.take_all_out_messages():
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
        def __init__(self):
            super(AgentBase.ReceiveMessage, self).__init__()

        async def run(self):
            try:
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

                if msg.receiver_session is not None:
                    self.agent.sessions[msg.receiver_session].add_message(msg)

                else:
                    self.agent.received_msg_without_session(msg)

            except Exception as e:
                logger.logger.log(
                    logger.EVENT_EXCEPTION,
                    where=f'Agent {self.agent.id} ReceiveMessage',
                    type=str(type(e)),
                    exception=str(e)
                )

    def __init__(self, agent_id, connections, config):
        self.id = agent_id
        self.connections = connections
        self.config = config
        self.policy = config.build_policy(self)

        self.jid = self.get_agent_jid(agent_id)

        self.session_lock = threading.Lock()
        self.sessions = {}
        self.next_session_id = 0

        self.sender_behaviour = None
        self.receiver_behaviour = None

        super(AgentBase, self).__init__(self.jid, self.jid)

    async def setup(self):
        self.sender_behaviour = self.SendMessages()
        self.receiver_behaviour = self.ReceiveMessage()

        self.add_behaviour(self.sender_behaviour)
        self.add_behaviour(self.receiver_behaviour)

        logger.logger.log(
            logger.EVENT_AGENT_STARTED,
            name=self.id,
            connection=', '.join(map(str, self.connections)),
            jid=self.jid,
            policy=self.config.get_policy_name()
        )

    def create_session(self):
        with self.session_lock:
            sess = Session(self, self.next_session_id)
            self.next_session_id += 1
            self.sessions[sess.session_id] = sess
            return sess

    def remove_session(self, session_id):
        with self.session_lock:
            self.sessions.pop(session_id)

    def get_sessions(self):
        with self.session_lock:
            return list(self.sessions.values())

    def received_msg_without_session(self, msg):
        sess = self.create_session()
        agent = msg.agent
        offer = msg.body
        agent_sess_id = msg.sender_session

        threading.Thread(target=self.run_transaction_in_client_mode, args=(agent, offer, sess, agent_sess_id)).run()

    def run_transaction_in_client_mode(self, agent, initial_offer, session, agent_session_id):
        session.end()
        # TODO

        raise NotImplementedError

    def run_transaction_in_server_mode(self, selling):
        session = self.create_session()
        # TODO
        session.end()

        raise NotImplementedError
