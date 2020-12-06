import sys, os, unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from unittest import TestCase
from client_oop import Client


class TestClientTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.bad_resp = '400 : Bad Request'
        self.good_resp = '200 : OK'

    def tearDown(self):
        pass

    def test_bad_response(self):
        self.assertEqual(self.client.presence_response({'response': 400, 'ERROR': 'Bad Request'}), self.bad_resp)

    def test_good_response(self):
        self.assertEqual(self.client.presence_response({'response': 200}), self.good_resp)

    def test_response_value_error(self):
        self.assertRaises(ValueError, self.client.presence_response, {'ERROR': 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
