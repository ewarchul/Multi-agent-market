import pickle
import base64
import spade.message as message


def deserialize_message(spade_message):
    return Message(
        spade_message.sender,
        pickle.loads(base64.b64decode(spade_message.body)),
        pickle.loads(base64.b64decode(spade_message.metadata['sender_session'])),
        pickle.loads(base64.b64decode(spade_message.metadata['receiver_session']))
    )


class Message(object):
    def __init__(self, agent, body, sender_session=None, receiver_session=None):
        self.agent = agent
        self.sender_session = sender_session
        self.receiver_session = receiver_session
        self.body = body

    def serialize(self):
        msg = message.Message(to=self.agent)
        msg.body = base64.b64encode(pickle.dumps(self.body)).decode('ascii')
        msg.metadata = dict(
            sender_session=base64.b64encode(pickle.dumps(self.sender_session)).decode('ascii'),
            receiver_session=base64.b64encode(pickle.dumps(self.receiver_session)).decode('ascii')
        )

        return msg
