import unittest, sys, os
sys.path.append(os.path.join(os.getcwd(), '..'))
from unittest import TestCase
from additionals.utils import send_msg, receive_msg
from additionals.settings import MAX_CONNECTIONS, DEFAULT_IP, DEFAULT_PORT, ENCODING, PACK_CAPACITY
import json


class TestSocket:
    def __init__(self, test_data):
        self.test_data = test_data

    def send(self, data):
        self.got_to_send = data

    def recv(self, size):
        self.prepare_to_encode = json.dumps(self.test_data)
        return self.prepare_to_encode.encode(ENCODING)


class TestUtilsTest(TestCase):

    def setUp(self):

        self.test_send_good = {
            'action': 'presence',
            'time': 1.1,
            'user': {
                'account_name': 'Guest'
            }
        }
        self.test_send_bad = {
            'action': 'presence',
            'time': 1.1,
            'user': {
                'account_name': 'unknown'
            }
        }
        self.test_rcv_good = {
            'response': 200
        }
        self.test_rcv_bad = {
            'response': 400,
            'ERROR': 'Bad Request'
        }
        #good
        self.prepare_to_encode_msg_good = json.dumps(self.test_send_good)
        self.encoded_msg_good = self.prepare_to_encode_msg_good.encode(ENCODING)
        #bad
        self.prepare_to_encode_msg_bad = json.dumps(self.test_send_bad)
        self.encoded_msg_bad = self.prepare_to_encode_msg_bad.encode(ENCODING)
        #sockets
        self.test_sock_send = TestSocket(self.test_send_good)
        self.test_sock_rcv_good = TestSocket(self.test_rcv_good)
        self.test_sock_rcv_bad = TestSocket(self.test_rcv_bad)

    def tearDown(self):
        pass

    def test_send_msg(self):
        send_msg(self.test_sock_send, self.test_send_good)
        self.assertEqual(self.encoded_msg_good, self.test_sock_send.got_to_send)

    def test_rcv_msg_good(self):
        self.assertEqual(receive_msg(self.test_sock_rcv_good), self.test_rcv_good)


if __name__ == '__main__':
    unittest.main()