import json
from .settings import ENCODING, PACK_CAPACITY
from .errors import IncorrectType, IncorrectDataToDecode
from additionals.decos import Log


@Log()
def send_msg(sock, message):
    """
    func to send message
    :param sock: connection socket
    :param message: dict
    :return:
    """
    msg_json = json.dumps(message)
    msg = msg_json.encode(ENCODING)
    sock.send(msg)


@Log()
def receive_msg(sender):
    """
    func to receive message
    :param sender: sender's socket
    :return: message dict
    """
    msg = sender.recv(PACK_CAPACITY)
    if isinstance(msg, bytes):
        msg_json = msg.decode(ENCODING)
        response = json.loads(msg_json)
        if isinstance(response, dict):
            return response
        raise IncorrectType
    raise IncorrectDataToDecode
