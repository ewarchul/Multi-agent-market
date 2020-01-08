import queue
import datetime

from agents.Message import Message


class Session(object):
    """
    Object for managing session
    """
    def __init__(self, agent, session_id):
        """
        Creates new session

        :param agent: owner
        :param session_id: id
        """
        self.agent = agent
        self.session_id = session_id

        self.out_queue = queue.Queue()
        self.in_queue = queue.Queue()

        self.ended = False

    def send(self, message_body, receiver, agent_session=None):
        """
        Prepares message to be sent

        :param message_body: object to be sent
        :param receiver: agent that the message is sent to
        :param agent_session: session id of receiver agent, None if no previous contact was made
        :return: None
        """
        msg = Message(self.agent.get_agent_jid(receiver), message_body, self.session_id, agent_session)
        self.out_queue.put(msg)

    def send_multiple(self, messages_body, receivers_sessions):
        """
        Prepares message to be sent to multiple receivers

        :param messages_body: object to be sent
        :param receivers_sessions: dict mapping agents to their sessions
        :return:
        """
        for r, s in receivers_sessions.items():
            self.send(messages_body, r, s)

    def receive(self, senders, timeout=None):
        """
        Receive messages from agents.

        Ignores unexpected messages

        :param senders: a collection of agents from whom messages are to be received
        :param timeout: timeout in seconds
        :return: list of agents that sent messages, list of sent objects, list of agents' session IDs
        """
        messages = {}
        end = datetime.datetime.now() + datetime.timedelta(seconds=timeout) if timeout else None
        dt = end - datetime.datetime.now() if end else None
        while len(messages) < len(senders) and (not timeout or dt.total_seconds() > 0):
            try:
                msg = self.in_queue.get(timeout=dt.total_seconds() if end else None)
                sender_id = self.agent.get_agent_id(msg.agent)
                if sender_id in senders:
                    messages[sender_id] = msg
            except queue.Empty:
                break

        messages = list(messages.values())
        senders = [self.agent.get_agent_id(m.agent) for m in messages]
        sessions = [m.sender_session for m in messages]

        return senders, [m.body for m in messages], sessions

    def add_in_message(self, msg):
        """
        Add received message
        :param msg: Message
        :return: None
        """
        self.in_queue.put(msg)

    def take_all_out_messages(self):
        """
        Allows to take all messages
        :return: Message object generator
        """
        while not self.out_queue.empty():
            try:
                yield self.out_queue.get(False)
            except queue.Empty:
                break

    def end(self):
        """
        Mark session as ended
        :return: None
        """
        self.ended = True
