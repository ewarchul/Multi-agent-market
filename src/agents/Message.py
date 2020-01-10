import pickle
import base64
import spade.message as message


def deserialize_message(spade_message):
    """
    Creates Message from spade message with sender as agent
    :param spade_message:
    :return:
    """
    return Message(
        str(spade_message.sender),
        pickle.loads(base64.b64decode(spade_message.body)),
        pickle.loads(base64.b64decode(spade_message.metadata['sender_session'])),
        pickle.loads(base64.b64decode(spade_message.metadata['receiver_session']))
    )


class Message(object):
    """
    Object to hold some non-text data and metadata
    """
    def __init__(self, agent, body, sender_session=None, receiver_session=None):
        """
        Creates message
        :param agent: the other side of the message
        :param body: body object
        :param sender_session: sender's session id
        :param receiver_session: receiver's session id
        """
        self.agent = agent
        self.sender_session = sender_session
        self.receiver_session = receiver_session
        self.body = body

    def serialize(self):
        """
        Serializes message to be sent with agent as receiver
        :return: spade message
        """
        msg = message.Message(to=self.agent)
        msg.body = base64.b64encode(pickle.dumps(self.body)).decode('ascii')
        msg.metadata = dict(
            sender_session=base64.b64encode(pickle.dumps(self.sender_session)).decode('ascii'),
            receiver_session=base64.b64encode(pickle.dumps(self.receiver_session)).decode('ascii')
        )

        return msg
