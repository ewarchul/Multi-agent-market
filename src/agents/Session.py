import queue
import datetime

from agents.Message import Message


class Session(object):
    def __init__(self, agent, session_id):
        self.agent = agent
        self.session_id = session_id

        self.out_queue = queue.Queue()
        self.in_queue = queue.Queue()

        self.ended = False

    def send(self, message_body, receiver, agent_session=None):
        msg = Message(self.agent.get_agent_jid(receiver), message_body, self.session_id, agent_session)
        self.out_queue.put_nowait(msg)

    def send_multiple(self, messages_body, receivers_sessions):
        for r, s in receivers_sessions.items():
            self.send(messages_body, r, s)

    def receive(self, n=1, timeout=None):
        messages = []
        end = datetime.datetime.now() + datetime.timedelta(seconds=timeout) if timeout else None
        dt = None

        while len(messages) < n:
            if end:
                dt = end - datetime.datetime.now()
                if dt.seconds <= 0:
                    break

            try:
                msg = self.in_queue.get(timeout=dt.seconds if end else None)
                messages.append(msg)
            except queue.Empty:
                break

        senders = [self.agent.get_agent_id(m) for m in messages]
        return senders, [m.body for m in messages]

    def add_in_message(self, msg):
        self.in_queue.put_nowait(msg)

    def take_all_out_messages(self):
        while not self.out_queue.empty():
            try:
                yield self.out_queue.get(False)
            except queue.Empty:
                break

    def end(self):
        self.ended = True
