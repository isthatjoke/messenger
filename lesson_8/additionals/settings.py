import logging

DEFAULT_PORT = 9035
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

# responses

RESPONSE_200 = {'response': 200}
RESPONSE_400 = {'response': 400, 'ERROR': 'Bad Request'}












