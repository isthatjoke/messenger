import logging

DEFAULT_PORT = 9350
DEFAULT_IP = '127.0.0.1'
PACK_CAPACITY = 1024     #max message length in bytes
MAX_CONNECTIONS = 5      #max client connections
ENCODING = 'utf-8'

# logging

LOGGING_LEVEL = logging.DEBUG



# JIM

ACTION = 'action'
PRESENCE = 'presence'
TIME = 'time'
ACCOUNT_NAME = 'account_name'
USER = 'user'
RESPONSE = 'response'
ERROR = 'ERROR'
MESSAGE = 'message'
SENDER = 'sender'
MESSAGE_TXT = 'mess_text'
TO = 'to'
FROM = 'from'
EXIT = 'exit'
RESPONSE_OK = '200 : OK'
GET_CONTACTS = 'get_contacts'
CONTACTS = 'contact_list'
ADD_CONTACT = 'add_contact'
REMOVE_CONTACT = 'remove_contact'
USERS_REQUEST = 'users_request'

# responses

RESPONSE_200 = {'response': 200}
RESPONSE_202 = {
    'response': 202,
    USERS_REQUEST: None
}
RESPONSE_203 = {
    'response': 203,
    GET_CONTACTS: None
}
RESPONSE_400 = {'response': 400, 'ERROR': 'Bad Request'}











