import sys, os

sys.path.append(os.path.join(os.getcwd(), '..'))
from unittest import TestCase
from server import Server
from additionals.settings import DEFAULT_PORT


class TestServerTest(TestCase):

    def setUp(self):
        self.server = Server('', DEFAULT_PORT)
        self.bad_dict = {
            'response': 400,
            'ERROR': 'Bad Request'
        }
        self.good_dict = {
            'response': 200
        }

    def tearDown(self):
        self.server.sock.close()

    def test_check_presence_wo_time(self):
        self.assertEqual(self.server.check_presence({
            'action': 'presence',
            'user': {
                'account_name': 'Guest'
            }
        }), self.bad_dict)

    def test_check_presence_wo_action(self):
        self.assertEqual(self.server.check_presence({
            'time': 1.1,
            'user': {
                'account_name': 'Guest'
            }
        }), self.bad_dict)

    def test_check_presence_wo_account_name(self):
        self.assertEqual(self.server.check_presence({
            'action': 'presence',
            'time': 1.1}), self.bad_dict)

    def test_check_presence_wrong_action(self):
        self.assertEqual(self.server.check_presence({
            'action': 'hello_world',
            'time': 1.1,
            'user': {
                'account_name': 'Guest'
            }
        }), self.bad_dict)

    def test_check_presence_wrong_name(self):
        self.assertEqual(self.server.check_presence({
            'action': 'presence',
            'time': 1.1,
            'user': {
                'account_name': 'new_one'
            }
        }), self.bad_dict)

    def test_check_presence_ok(self):
        self.assertEqual(self.server.check_presence({
            'action': 'presence',
            'time': 1.1,
            'user': {
                'account_name': 'Guest'
            }
        }), self.good_dict)


if __name__ == '__main__':
    unittest.main()
